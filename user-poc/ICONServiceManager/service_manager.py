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
import sys
import json
from time import sleep
import requests

from iconsdk.icon_service import IconService
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.builder.transaction_builder import CallTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.signed_transaction import SignedTransaction

SLEEP_TIMER = 5
STEP_LIMIT = 10000000000
NONCE = 100


class ServiceManager:
    def __init__(self, node_conf_path: str, wallet_path: str, passwd: str):

        # Node configuration to be connected
        with open(node_conf_path, "r") as f:
            node_conf = json.load(f)

        self._my_chain_name = node_conf["chain_name"]
        self._nid = int(node_conf["nid"], 16)

        self.web_protocol = node_conf["web_protocol"]

        if self.web_protocol == "ssl":
            self._icon_service = IconService(HTTPProvider("https://"+node_conf["address"], 3))
            self._ws_block = f"wss://{node_conf['address']}/api/ws/{node_conf['channel']}"
        elif self.web_protocol == "http":
            self._icon_service = IconService(HTTPProvider("http://"+node_conf["address"], 3))
            self._ws_block = f"ws://{node_conf['address']}/api/node/{node_conf['channel']}"
        else:
            print("[error] Not supported web_protocol")
            sys.exit()

        # Set wallet of actor
        self._wallet = KeyWallet.load(wallet_path, passwd)

        self._score_info = node_conf["scores"]

    # TODO 실제로는 없어도 되는 method
    def get_block(self, value=None) -> dict:
        block = self._icon_service.get_block(value)
        return block

    def get_rep_list(self):
        resp = self.query("cx0000000000000000000000000000000000000000", "getPRepTerm", {})
        preps_info = resp["preps"]
        preps_list = []
        for item in preps_info:
            preps_list.append(item["address"])

        return preps_list

    def get_rep_list_local(self):
        node_info = f"http://localhost:9100/api/node"
        
        headers = {
            "content-type": "application/json"
        }
        body = {
            "jsonrpc": "2.0",
            "method": "node_getChannelInfos",
            "id": 1234
        }
        resp = requests.post(node_info, data=json.dumps(body), headers=headers).json()

        assert resp["jsonrpc"]
        assert resp["id"]

        preps_list = []
        for item in resp["result"]["channel_infos"]["icon_dex"]["peers"]:
            preps_list.append(item["id"])
        
        return preps_list

    def get_tx_result_by_hash(self, tx_hash: str) -> dict:
        tx_result = self._icon_service.get_transaction_result(tx_hash)
        # print(f"tx_result: {tx_result}")
        for key, value in tx_result.items():
            if isinstance(value, int):
                tx_result[key] = hex(value)

        try:
            tx_result["logsBloom"] = "0x"+tx_result["logsBloom"].hex()
        except KeyError:
            pass

        return tx_result

    def call_tx(self, score_addr: str, method: str, params: dict) -> dict:
        transaction = CallTransactionBuilder() \
            .from_(self._wallet.get_address()) \
            .to(score_addr) \
            .step_limit(STEP_LIMIT) \
            .nid(self._nid) \
            .nonce(NONCE) \
            .method(method) \
            .params(params) \
            .build()
        return self._send_transaction(transaction)

    def query(self, score_addr: str, method: str, params: dict):
        query = CallBuilder() \
            .from_(self._wallet.get_address()) \
            .to(score_addr) \
            .method(method) \
            .params(params) \
            .build()
        return self._icon_service.call(query)

    def dummy_tx_send(self, loop: int):
        for i in range(loop):
            transaction = CallTransactionBuilder().\
                from_(self._wallet.get_address()).\
                to(self._wallet.get_address()).\
                step_limit(STEP_LIMIT).\
                value(1).\
                nid(self.nid).\
                nonce(NONCE).\
                method("transfer").build()

            signed_tx = SignedTransaction(transaction, self._wallet)
            tx_hash = self.icon_service.send_transaction(signed_tx)
            print(f"[dc_log] dummy tx hash: {tx_hash}")

    def _send_transaction(self, transaction) -> dict:
        signed_tx = SignedTransaction(transaction, self._wallet)
        tx_hash = self._icon_service.send_transaction(signed_tx)

        sleep(SLEEP_TIMER)
        return self.get_tx_result_by_hash(tx_hash)

    @staticmethod
    def print_result(data: dict):

        print("----------------------------------------------------------------------------------")
        print("<Tx_result>")
        print(f" -    txHash: {data['txHash']}")
        print(f" -    height: {data['blockHeight']}")
        print(f" - blockHash: {data['blockHash']}")
        try:
            print(f" - scoreAddr: {data['scoreAddress']}")
        except KeyError:
            pass
        print(f" -  stepUsed: {data['stepUsed']}")
        print(f" -    status: {data['status']}")
        print("----------------------------------------------------------------------------------\n\n")


    @property
    def ws_addr(self):
        return self._ws_block

    @property
    def chain_name(self):
        return self._my_chain_name

    @property
    def nid(self):
        return self._nid

    @property
    def from_account(self):
        return self._wallet.get_address()

    @property
    def icon_service(self):
        return self._icon_service



