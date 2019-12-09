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


class TokenFallbackInterface(InterfaceScore):
    @interface
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        pass


class ForeignerToken(IconScoreBase):

    @eventlog
    def Log(self, msg: str):
        pass

    @eventlog
    def Mint(self, _to: Address, _value: int, _data: bytes):
        pass

    @eventlog
    def Transfer(self, _to: Address, _value: int, _data: bytes):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._balance = DictDB("balance", db, int)
        self._bmc_addr = VarDB("bmc_addr", db, Address)

    @external
    def on_install(self) -> None:
        super().on_install()

    @external
    def on_update(self) -> None:
        super().on_update()

    @external
    def set_bmc(self, bmc_addr: Address):
        self._bmc_addr.set(bmc_addr)

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balance[_owner]

    @external
    def mint(self, _to: Address, _value: int, _data: bytes = None):

        if not self._bmc_addr.get():
            revert(f"bmc addr is not set")

        if self.msg.sender != self._bmc_addr.get():
            revert("Only BMC can do mint")

        print(f"[eps] value: {_value}, {type(_value)}")

        if _value < 0:
            revert(f"Invalid param {_value}")

        self._balance[_to] = self._balance[_to] + _value
        self.Mint(_to, _value, _data)

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):

        print("[eps] im in transfer of intertoken")
        if _value < 0:
            revert(f"Invalid param {_value}")
        expect_sender_balance = self._balance[self.msg.sender] - _value
        if expect_sender_balance < 0:
            revert("Out of balacne")
        self._balance[self.msg.sender] = expect_sender_balance
        self._balance[_to] = self._balance[_to] + _value
        if _to.is_contract:
            recipient_score = self.create_interface_score(_to, TokenFallbackInterface)
            recipient_score.tokenFallback(self.msg.sender, _value, _data)
        self.Transfer(_to, _value, _data)
        print("[eps] after Transfer(eventLog)")

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balance[_owner]
