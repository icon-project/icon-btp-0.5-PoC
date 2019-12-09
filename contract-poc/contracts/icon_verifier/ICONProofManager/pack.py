# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# TODO: after score supports msgpack, this pack method will be replaced to msgpack

def btp_poe_pack(json_dump, receipt, rp_proof: list, block_msg: list, votes: list) -> str:
    # 1.
    packed_receipt = receipt_pack(json_dump, receipt)
    packed_rp_proof = receipt_proof_pack(rp_proof)
    packed_block_msg = block_pack(block_msg)
    packed_votes = votes_pack(json_dump, votes)

    ret = {
        "receipt": packed_receipt,
        "rp_proof": packed_rp_proof,
        "block_msg": packed_block_msg,
        "votes": packed_votes
    }
    return json_dump(ret)


def btp_poe_unpack(json_load, packed_poe) -> list:
    poe = json_load(packed_poe)
    packed_receipt = poe["receipt"]
    packed_rp_proof = poe["rp_proof"]
    packed_block_msg = poe["block_msg"]
    packed_votes = poe["votes"]

    receipt = receipt_unpack(json_load, packed_receipt)
    rp_proof = receipt_proof_unpack(packed_rp_proof)
    block_msg = block_unpack(packed_block_msg)
    votes = votes_unpack(json_load, packed_votes)

    return [receipt, rp_proof, block_msg, votes]


def reps_list_poe_pack(json_dump, reps_list: list, block_msg: list, votes: list) -> str:
    packed_reps_list = reps_list_pack(reps_list)
    packed_block_msg = block_pack(block_msg)
    packed_votes = votes_pack(json_dump, votes)

    ret = {
        "reps_list": packed_reps_list,
        "block_msg": packed_block_msg,
        "votes": packed_votes
    }
    return json_dump(ret)


def rep_list_poe_unpack(json_load, packed_poe: str) -> list:
    poe = json_load(packed_poe)
    packed_reps_list = poe["reps_list"]
    packed_block_msg = poe["block_msg"]
    packed_votes = poe["votes"]

    reps_list = reps_list_unpack(packed_reps_list)
    block_msg = block_unpack(packed_block_msg)
    votes = votes_unpack(json_load, packed_votes)

    return [reps_list, block_msg, votes]


def receipt_pack(json_dump, receipt) -> str:
    return json_dump(receipt)


def receipt_unpack(json_load, packed_receipt) -> dict:
    return json_load(packed_receipt)


def receipt_proof_pack(rp_proof: list) -> str:
    packed_rp_proof = ""
    for proof in rp_proof:
        for key, item in proof.items():
            packed_rp_proof += "." + key + "." + item.hex()
    return packed_rp_proof[1:]


def receipt_proof_unpack(packed_rp_proof: str) -> list:
    tmp = list(str(packed_rp_proof).split("."))

    rp_proof = []
    for i in range(len(tmp)//2):
        rp_proof.append({
            tmp[2*i]: bytes.fromhex(tmp[2*i+1])
        })
    return rp_proof


def block_pack(block_hash_origin: list) -> str:
    packed_block_msg = ""
    for i in range(len(block_hash_origin)):
        if isinstance(block_hash_origin[i], bytes):
            packed_block_msg += "." + block_hash_origin[i].hex()
        elif isinstance(block_hash_origin[i], int):
            packed_block_msg += "." + hex(block_hash_origin[i])

    return packed_block_msg[1:]


def block_unpack(packed_block_msg: str) -> list:
    val_list = packed_block_msg.split(".")
    block_msg = []
    for item in val_list:
        if item[:2] == "0x":
            block_msg.append(int(item, 16))
        else:
            tmp = bytes.fromhex(item)
            block_msg.append(tmp)
    return block_msg


def votes_pack(json_dump, votes: list) -> str:
    tmp = {}
    for idx, item in enumerate(votes):
        tmp[hex(idx)] = item[0] + "." + hex(item[1]) + "." + item[2].hex()

    packed = json_dump(tmp)
    return packed


def votes_unpack(json_load, packed_votes: str) -> list:
    votes_dict = json_load(packed_votes)
    votes_list = []
    for key, value in votes_dict.items():
        tmp = value.split(".")
        tmp[1] = int(tmp[1], 16)
        tmp[2] = bytes.fromhex(tmp[2])
        votes_list.append(tmp)
    return votes_list


def reps_list_pack(rep_list: list) -> str:
    packed = ""
    for item in rep_list:
        packed += "."+item
    return packed[1:]


def reps_list_unpack(packed_reps_list: str) -> list:
    return packed_reps_list.split(".")




