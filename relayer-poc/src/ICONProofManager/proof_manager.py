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

from .types import Hash32
from .merkle_tree import MerkleTree
from .hash_generator import HashOriginGeneratorV1


class ProofManager:
    def __init__(self, sha3_256, values: list, type_: str):
        self.type = type_
        self.sha3_256 = sha3_256
        self.hashes = [self.to_hash32(value) for value in values] if values else []
        self._merkle_tree = MerkleTree(sha3_256)

    def get_proof(self, hash_or_index) -> list:
        if isinstance(hash_or_index, bytes):
            index = self.hashes.index(hash_or_index)
        else:
            index = hash_or_index

        if not self._merkle_tree.is_ready:
            self.make_tree()
        return self._merkle_tree.get_proof(index)

    def get_proof_root(self) -> Hash32:
        if not self._merkle_tree.is_ready:
            self.make_tree()
        root = self._merkle_tree.get_merkle_root()
        return Hash32(root) if root is not None else Hash32.empty()

    @classmethod
    def validate_proof(cls, sha3_256, hash_: Hash32, root_hash: Hash32, proof: list) -> bool:
        """ Don't have to init a trie"""
        return MerkleTree.validate_proof(sha3_256, proof, hash_, root_hash)

    def make_tree(self):
        self._merkle_tree.reset_tree()
        self._merkle_tree.add_leaf(self.hashes)
        self._merkle_tree.make_tree()

    def to_hash32(self, value):
        if value is None:
            return Hash32.empty()
        elif isinstance(value, Hash32):
            return value
        elif isinstance(value, (bytes, bytearray)) and len(value) == 32:
            return Hash32(value)
        if isinstance(value, bool):
            value = b'\x01' if value else b'\x00'
        elif isinstance(value, int):
            if value < 0:
                raise RuntimeError(f"value : {value} is negative.")
            value = value.to_bytes((value.bit_length() + 7) // 8, "big")
        elif isinstance(value, dict):
            salt = ""
            if self.type == "Receipt":
                value = dict(value)
                value.pop("failure", None)
                value.pop("blockHash", None)
                salt = "icx_receipt"
            if self.type == "Vote":
                value = dict(value)
                value.pop("signature", None)
                salt = "icx_vote"

            hash_generator = HashOriginGeneratorV1()
            value = salt + "." + hash_generator.generate(value)
            value = value.encode()

        return Hash32(self.sha3_256(value))

