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


from iconservice import *
from .ICONProofManager.proof_manager import ProofManager
from .ICONProofManager.pack import btp_poe_unpack, rep_list_poe_unpack, reps_list_unpack


class IconVerifier(IconScoreBase):

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self.reps_list = ArrayDB("reps_list", db, str)

    def on_install(self, packed_rep_list: str) -> None:
        super().on_install()

        reps_list = reps_list_unpack(packed_rep_list)
        print(f"[dc_log] reps_list: {reps_list}")
        for rep in reps_list:
            self.reps_list.put(rep)

    def on_update(self) -> None:
        super().on_update()

    # TODO method for validateor list update
    @external
    def set_validators(self, packed_poe: str):
        
        next_reps, block_msg, votes = rep_list_poe_unpack(json_loads, packed_poe)
        fomatted_next_reps= []
        for rep in next_reps:
            fomatted_next_reps.append(b'\x00'+bytes.fromhex(rep[2:]))

        print(f"[dc_log] next_reps: {fomatted_next_reps}")

        reps_pm = ProofManager(sha3_256, fomatted_next_reps, "")
        next_reps_hash = reps_pm.get_proof_root()

        if block_msg[5] != next_reps_hash:
            revert(f"[Verifier ERROR] Invalid reps_list")

        block_pm = ProofManager(sha3_256, block_msg, "")
        block_hash = block_pm.get_proof_root()

        votes_msg = list()
        for idx, vote in enumerate(votes):
            vote_msg = {
                "rep": self.reps_list[idx],
                "timestamp": vote[0],
                "blockHeight": hex(block_msg[9]),
                "round_": vote[1],
                "blockHash": "0x" + block_hash.hex()
            }
            votes_msg.append(vote_msg)

        vpm = ProofManager(sha3_256, votes_msg, "Vote")

        for idx, hash_ in enumerate(vpm.hashes):
            key = recover_key(hash_, votes[idx][2])
            addr = create_address_with_key(key)

            print("rep in score: ", self.reps_list[idx])
            print("calculated :  ", str(addr))

            if self.reps_list[idx] != str(addr):
                revert(f"[Verifier] comparison fail!!")

        print(f"[verifier] comparison succccccc!!")

        while self.reps_list.pop():
            pass

        ret = ""
        for e in self.reps_list:
            ret += e
        print(f"[dc_log] after pop replist:{ret}")

        for item in next_reps:
            self.reps_list.put(item)

        ret = ""
        for e in self.reps_list:
            ret += "."+e
        print(f"[dc_log] after set replist:{ret[1:]}")


    @external
    # def verify_btp_msg(self, receipt: bytes, rp_proof: bytes, block_msg: bytes, sigs: bytes):
    def verify_btp_msg(self, packed_poe: str):
        """ verifies received btp-msg"""
        # print(f"[verifier] packed_poe: {packed_poe}")
        # poe = unpackb(packed_poe, allow_invalid_utf8=True)
        poe = btp_poe_unpack(json_loads, packed_poe)

        receipt = poe[0]
        rp_proof = poe[1]
        block_msg = poe[2]
        sigs = poe[3]

        btp_msg = ""
        for event in receipt["eventLogs"]:
            # TODO 상대 BMC 주소 확인하는 로직 구현 필요
            if event["indexed"][0] == "Message(str)":
                btp_msg = event["data"][0]

        if not btp_msg:
            revert(f"No btp_msg")

        rpm = ProofManager(sha3_256, [receipt], "Receipt")
        if not rpm.validate_proof(sha3_256, rpm.hashes[0], block_msg[2], rp_proof):
            revert(f"Fail to validate receipt merkle path")

        bpm = ProofManager(sha3_256, block_msg, "Block")
        block_hash = bpm.get_proof_root()

        votes_msg = list()
        for idx, sig in enumerate(sigs):
            vote_msg = {
                "rep": self.reps_list[idx],
                "timestamp": sig[0],
                "blockHeight": hex(block_msg[9]),
                "round_": sig[1],
                "blockHash": "0x" + block_hash.hex()
            }
            votes_msg.append(vote_msg)

        vpm = ProofManager(sha3_256, votes_msg, "Vote")

        for idx, hash_ in enumerate(vpm.hashes):
            key = recover_key(hash_, sigs[idx][2])
            addr = create_address_with_key(key)

            print("rep in score: ", self.reps_list[idx])
            print("calculated :  ", str(addr))

            if self.reps_list[idx] != str(addr):
                revert(f"[Verifier] comparison fail!!")

        print(f"[Verifier] comparison succccccc!!")
        return btp_msg





