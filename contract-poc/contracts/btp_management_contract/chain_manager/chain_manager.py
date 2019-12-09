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

from ..bases.reverts import *
from ..bases.json_object import JsonObject, Attribute, AddressAttr
from ..interfaces.verifier_interface import VerifierInterface


class ChainInfo(JsonObject):
    verifier = AddressAttr("verifier")
    description = Attribute("description")

    @classmethod
    def from_string(cls, dumped_obj):
        obj = cls()
        obj.set_from_dict(json_loads(dumped_obj))
        for name, value in obj._attributes.items():
            setattr(obj, name, value)
        return obj


class ChainManager:
    def __init__(self, db: IconScoreDatabase, bmc):
        self._db = db
        self._bmc_home = VarDB("my_chain_id", db, str)
        self._chain_info = DictDB("chain_info", db, str)  # list of chain info.
        self._bmc = bmc  # instance of bmc which the chain manager belongs to.

    def register(self, name: str, verifier: Address, description: str):
        """Register another chain"""
        if not verifier.is_contract:
            InvalidAddressRevert(address=verifier)

        # double registration check
        if self._chain_info[name]:
            RegisteredChainRevert(chain=name)

        chain_info = ChainInfo.json_build(
            verifier=verifier,
            decription=description
        )
        self._chain_info[name] = str(chain_info)

    def set_my_chain(self, chain_name):
        self._bmc_home.set(chain_name)

    def get_chain_info(self, name) -> ChainInfo:
        try:
            info = self._chain_info[name]
            return ChainInfo.from_string(info)
        except KeyError:
            UnknownChainRevert("[BMC] unknown chain name")

    def get_bmc_home(self) -> str:
        return self._bmc_home.get()

    def is_home(self, name: str):
        if name == self._bmc_home.get():
            return True
        return False

    def get_verifier(self, name: str) -> VerifierInterface:
        try:
            chain_info = self.get_chain_info(name)
        except IconScoreException as error:
            UnknownChainRevert(error)

        return self._bmc.create_interface_score(chain_info.verifier, VerifierInterface)
