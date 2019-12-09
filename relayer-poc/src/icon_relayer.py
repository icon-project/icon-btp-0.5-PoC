# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Class for websocket client between child(citizen) node and mother peer"""
import json
import logging
import websockets
import hashlib
import ssl


from base64 import b64decode
from websockets.exceptions import InvalidStatusCode, InvalidMessage

from ICONServiceManager.chain_manager import ChainManager
from ICONProofManager.proof_manager import ProofManager
from ICONProofManager.pack import btp_poe_pack, reps_list_poe_pack

ADMIN_WALLET_PATH = "../config/wallets/_________________________CREATOR.wallet"
PASSWD = "test"


class IconRelayer:

    def __init__(self, sender_chain_path: str, receiver_chain_path: str):
        self._src_chain = ChainManager(sender_chain_path, ADMIN_WALLET_PATH, PASSWD)
        self._dst_chain = ChainManager(receiver_chain_path, ADMIN_WALLET_PATH, PASSWD)

    async def start(self):
        ssl_context = ssl.SSLContext()

        last_block_height = self._src_chain.get_block("latest")["height"]
        print(f" [Relayer] last block height : {last_block_height}")

        request = {
            "jsonrpc": "2.0",
            "method": "node_ws_Subscribe",
            "params": {
                "height": last_block_height,
                "peer_id": "hx0"
            },
            "id": 1
        }

        try:
            if self._src_chain.web_protocol == "ssl":
                async with websockets.connect(self._src_chain.ws_addr, ssl=ssl_context) as websocket:
                    await websocket.send(json.dumps(request))
                    await self._subscribe_loop(websocket)
            elif self._src_chain.web_protocol == "http":
                async with websockets.connect(self._src_chain.ws_addr) as websocket:
                    await websocket.send(json.dumps(request))
                    await self._subscribe_loop(websocket)
            else:
                print("[error] Not Supported web_protocol")

        except (InvalidStatusCode, InvalidMessage) as e:
            logging.warning(f"websocket subscribe {type(e)} exception, caused by: {e}\n"
                            f"This target({self._src_chain.ws_addr}) may not support websocket yet.")
            raise NotImplementedError
        except Exception as e:
            # traceback.print_exc()
            logging.error(f"websocket subscribe exception, caused by: {type(e)}, {e}")
            raise ConnectionError

    async def _subscribe_loop(self, websocket):
        prev_block = {}

        while True:
            tmp = await websocket.recv()
            resp = json.loads(tmp)

            if resp["method"] == "node_ws_PublishNewBlock":
                await self._process_event(prev_block, resp["params"]["block"])
                prev_block = resp["params"]["block"]

    async def _process_event(self, current_block: dict, next_block):

        if not current_block:
            return

        receipts_list, index = self.search_btp_msg(current_block)
        if index >= 0:
            self._process_btp_msg(current_block, next_block, receipts_list, index)

        if current_block["nextRepsHash"] != "0x0000000000000000000000000000000000000000000000000000000000000000":
            self._process_validator_update(current_block, next_block)

    def _process_btp_msg(self, current_block: dict, next_block: dict, receipts_list: list, index: int):

        # 2. PoE 생성
        rp_proof = self.gen_receipt_proof(receipts_list, index)
        block_msg = self.gen_block_proof(current_block)
        compressed_votes = self.gen_vote_proof(next_block)

        packed_poe = btp_poe_pack(json.dumps, receipts_list[index], rp_proof, block_msg, compressed_votes)
        print(f"packed_poe: {packed_poe}")

        params = {
            "from_chain": self._src_chain.chain_name,
            "packed_poe": packed_poe
        }
        tx_result = self._dst_chain.call_tx(self._dst_chain.bmc, "relayMessage", params)
        self._dst_chain.print_result(tx_result)

    def _process_validator_update(self, current_block: dict, next_block:dict):

        if self._src_chain.chain_name == "EuljiroTestnet":
            reps_list = self._src_chain.get_rep_list()
        else:
            reps_list = self._src_chain.get_rep_list_local()

        block_proof = self.gen_block_proof(current_block)
        votes_proof = self.gen_vote_proof(next_block)

        packed_poe = reps_list_poe_pack(json.dumps, reps_list, block_proof, votes_proof)
        print(f"packed_poe: {packed_poe}")

        tx_result = self._dst_chain.call_tx(self._dst_chain.verifier, "set_validators", {"packed_poe": packed_poe})
        self._dst_chain.print_result(tx_result)

    def search_btp_msg(self, block: dict):
        receipts_list = []
        index = 0
        found = False

        try:
            block["transactions"]
        except KeyError:
            return [], -1

        for idx, tx in enumerate(block["transactions"]):
            tx_hash = "0x"+tx["txHash"]
            resp = self._src_chain.get_tx_result_by_hash(tx_hash)
            resp["txHash"] = resp["txHash"][2:]

            for event in resp["eventLogs"]:
                if event["scoreAddress"] != self._src_chain.bmc:
                    continue
                if event['indexed'][0] == 'Message(str)':
                    found = True
                    index = idx

            receipts_list.append(resp)
        if found:
            return receipts_list, index
        else:
            return [], -1

    @staticmethod
    def gen_receipt_proof(receipts_list: list, index: int) -> list:
        rp = ProofManager(sha3_256, receipts_list, "Receipt")
        target_hash = rp.to_hash32(receipts_list[index])
        rp_proof = rp.get_proof(target_hash)
        return rp_proof

    @staticmethod
    def gen_block_proof(block: dict):

        ret = list()
        ret.append(bytes.fromhex(block["prevHash"][2:]))
        ret.append(bytes.fromhex(block["transactionsHash"][2:]))
        ret.append(bytes.fromhex(block["receiptsHash"][2:]))
        ret.append(bytes.fromhex(block["stateHash"][2:]))
        ret.append(bytes.fromhex(block["repsHash"][2:]))
        ret.append(bytes.fromhex(block["nextRepsHash"][2:]))
        ret.append(bytes.fromhex(block["leaderVotesHash"][2:]))
        ret.append(bytes.fromhex(block["prevVotesHash"][2:]))
        ret.append(bytes.fromhex(block["logsBloom"][2:]))
        ret.append(int(block["height"], 16))
        ret.append(int(block["timestamp"], 16))
        ret.append(bytes.fromhex(block["leader"][2:]))
        ret.append(bytes.fromhex(block["nextLeader"][2:]))
        return ret

    @staticmethod
    def gen_vote_proof(next_block: dict):
        votes_origin = next_block["prevVotes"]

        compressed_votes = list()
        for vote in votes_origin:
            decoded_sig = b64decode(vote["signature"])
            compressed_votes.append([vote["timestamp"], vote["round_"], decoded_sig])

        return compressed_votes


def sha3_256(value: bytes):
    return hashlib.sha3_256(value).digest()



