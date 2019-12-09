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


class InvalidParamRevert:
    def __new__(cls, cause):
        revert(f"invalid param: {cause}", 1001)


class TokenFallbackInterface(InterfaceScore):
    @interface
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        pass


class Irc2Sample(IconScoreBase):

    @eventlog
    def Transfer(self, _to: Address, _value: int, _data: bytes):
        pass

    @eventlog
    def Faucet(self, _owner: Address):
        pass

    @eventlog
    def Debug(self, _value: int):
        pass

    _BALANCES = 'balances'
    _TOTAL_SUPPLY = 'total_supply'
    _DECIMALS = 'decimals'

    # @eventlog(indexed=3)
    # def Transfer(self, _to: Address, _value: int, _data: bytes):
    #     pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)

    def on_install(self) -> None:
        super().on_install()

        self._total_supply.set(100000)
        self._balances[self.msg.sender] = 100000

    def on_update(self) -> None:
        super().on_update()

    @external
    def faucet(self):
        self._balances[self.msg.sender] += 10000
        self.Faucet(self.msg.sender)

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balances[_owner]

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        if _value < 0:
            revert(f"Invalid param {_value}")

        # to_addr = Address.from_string(_to)

        expect_sender_balance = self._balances[self.msg.sender] - _value
        if expect_sender_balance < 0:
            revert("[transfer] Out of balance")
        self._balances[self.msg.sender] = expect_sender_balance
        self._balances[_to] = self._balances[_to] + _value
        if _to.is_contract:
            recipient_score = self.create_interface_score(_to, TokenFallbackInterface)
            recipient_score.tokenFallback(self.msg.sender, _value, _data)

        self.Transfer(_to, _value, _data)


