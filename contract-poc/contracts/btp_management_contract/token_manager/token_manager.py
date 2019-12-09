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
# Token manager of BMC.
# Token manager has all of available Token bank for btp transfer.
# When client requests to send A Token in srcChain to client of dstChain,
# balance[receiver] in BMC of dstChain increases, while balance[sender] in BMC of srcChain decreases.
# from json import JSONDecodeError

from iconservice import *

from ..chain_manager.chain_manager import ChainManager
from ..interfaces.irc2 import Irc2
from ..interfaces.foreignertoken import ForeignerToken
from ..bases.json_object import JsonObject
from ..bases.reverts import *
from ..token_manager.token_bank import Bank


class TokenInfo(JsonObject):

    def __init__(self, token_home: str, token_name: str, std: str, token_addr: Address):
        super().__init__()
        self._token_home = token_home
        self._token_name = token_name
        self._std = std
        self._token_addr = token_addr


class TokenManager:
    def __init__(self, db: IconScoreDatabase, chain_manager: ChainManager, bmc):
        self._token_bank = Bank("token", db)
        self._standards = DictDB("token_standards", db, str)
        self._token_info = DictDB("token_info", db, str)

        self._chain_manager = chain_manager
        self._bmc = bmc

    def register_standard(self, standard: str, transfer_params: str):  # TODO transfer_params는 무엇??
        if self._standards[standard]:
            revert(f"Duplicated Token Standard:{standard}")
        else:
            self._standards[standard] = transfer_params

    def register_token(self, token_home: str, token_name: str, std_name: str, token_score_addr: Address):

        if self._token_info[token_score_addr] or self._token_info[f"{token_home}#{token_name}"]:
            RegisteredTokenRevert(token=f"{token_home}#{token_name}")
        else:
            self._token_info[f"{token_home}#{token_name}"] = f"{std_name}#{token_score_addr}"
            self._token_info[str(token_score_addr)] = f"{token_home}#{token_name}"
            self._bmc.RegisterToken(token_home, token_name, std_name, token_score_addr)

    def get_token_id(self, token_addr: Address) -> list:
        try:
            return self._token_info[str(token_addr)].split("#")
        except KeyError:
            return ["", ""]

    def get_token_addr(self, token_home: str, token_name: str) -> Address:
        addr = self._token_info[f"{token_home}#{token_name}"].split("#")[1]
        return Address.from_string(addr)

    def deposit(self, from_account: Address, amount: int, token_addr: Address = None):
        if token_addr is None:
            token_name = "ICX"
            token_home = self._chain_manager.get_bmc_home()
        else:
            token_home, token_name = self.get_token_id(token_addr)

        if (not token_home) or (not token_name):
            UnknownTokenRevert(token_home, token_name)

        self._token_bank.deposit(token_home, token_name, from_account, amount)
        self._bmc.Deposit(token_home, token_name, from_account, amount)

    def get_balance(self, token_home: str, token_name: str, account: Address, label: str) -> int:
        target_bank = self.get_bank()
        if label == "":
            return target_bank.balanceOf(token_home, token_name, account)
        else:
            return target_bank.lockedBalanceOf(token_home, token_name, account)

    def get_bank(self) -> Bank:
        return self._token_bank

    def withdraw(self, token_home: str, token_name: str, target_account: Address, amount: int):
        if amount <= 0:
            InvalidParamRevert(f"Amount must be over 0 but {amount}")

        if not self._token_info[f"{token_home}#{token_name}"] and not self._is_icx(token_home, token_name):
            UnknownTokenRevert(token_home, token_name)

        if self._token_bank.burn(token_home, token_name, target_account, amount):
            if self._is_icx(token_home, token_name):
                self._bmc.icx.transfer(target_account, amount)
            else:
                self._withdraw_token(token_home, token_name, target_account, amount)
            self._bmc.Withdraw(token_home, token_name, str(target_account), amount)
        else:
            OutOfBalanceRevert(amount, self._token_bank.balanceOf(token_home, token_name, target_account))

    def _withdraw_token(self, token_home: str, token_name: str, target_account: Address, amount: int):

        # token_info = TokenInfo.from_string(self._token_info[f"{_tokenHome}#{_tokenName}"])
        token_addr = self.get_token_addr(token_home, token_name)

        if self._chain_manager.is_home(token_home):
            token = self._bmc.create_interface_score(token_addr, Irc2)
        else:
            token = self._bmc.create_interface_score(token_addr, ForeignerToken)
        token.transfer(target_account, amount)

    def _is_icx(self, home, name):
        return self._chain_manager.is_home(home) and name == "ICX"

