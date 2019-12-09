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
#
# Token bank provides methods which modify balance managed in token manager of BMC
from iconservice import *
from ..bases.reverts import *


class Bank:

    def __init__(self, name: str, db: IconScoreDatabase):
        self._name = name
        self._db = db
        self._balance = DictDB(f"{name}_bank", db, int, 3)  # [token_home][token_name][account]
        self._locked_balance = DictDB(f"{name}_lock_bank", db, int, 3)  # [token_home][token_name][account]

    def deposit(self, token_home: str, token_name: str, target_account: Address, amount: int) -> bool:
        if amount < 0:
            InvalidParamRevert(f"Amount must be over 0 but {amount}")

        addr_ = str(target_account)
        self._balance[token_home][token_name][addr_] = self._balance[token_home][token_name][addr_] + amount
        return True

    def burn(self, token_home: str, token_name: str, target_account: Address, amount: int) -> bool:
        addr_ = str(target_account)
        expect_balance = self._balance[token_home][token_name][addr_] - amount

        if expect_balance >= 0:
            self._balance[token_home][token_name][addr_] = expect_balance
            return True
        return False

    def lockToken(self, token_home: str, token_name: str, target_account: Address, amount: int) -> bool:
        addr_ = str(target_account)

        if self._locked_balance[token_home][token_name][addr_]:
            self._locked_balance[token_home][token_name][addr_] = self._locked_balance[token_home][token_name][
                                                                      addr_] + amount
        else:
            self._locked_balance[token_home][token_name][addr_] = amount

        # self._locked_balance[token_home][token_name][addr_] += amount
        return self.burn(token_home, token_name, target_account, amount)

    def unlockToken(self, token_home: str, token_name: str, target_account: Address, amount: int) -> bool:
        addr_ = str(target_account)
        expected = self._locked_balance[token_home][token_name][addr_] - amount
        if expected >= 0:
            self._locked_balance[token_home][token_name][addr_] = expected
            return True
        return False

    def rollBack(self, token_home: str, token_name: str, target_account: Address, amount: int) -> bool:
        addr_ = str(target_account)

        if not self.unlockToken(token_home, token_name, target_account, amount):
            OutOfBalanceRevert(amount, self._locked_balance[token_home][token_name][addr_])

        if not self.deposit(token_home, token_name, target_account, amount):
            OutOfBalanceRevert(amount, self._balance[token_home][token_name][addr_])

        return True

    def balanceOf(self, token_home: str, token_name: str, target_account: Address) -> int:
        addr_ = str(target_account)
        return self._balance[token_home][token_name][addr_]

    def lockedBalanceOf(self, token_home: str, token_name: str, target_account: Address) -> int:
        return self._locked_balance[token_home][token_name][str(target_account)]