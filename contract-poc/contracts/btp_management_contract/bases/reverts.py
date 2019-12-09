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
from iconservice import revert


class InvalidAddressRevert:
    def __new__(cls, address):
        revert(f"Invalid address {address}", 1000)


class InvalidParamRevert:
    def __new__(cls, cause):
        revert(f"invalid param: {cause}", 1001)


class UnauthorizedUser:
    def __new__(cls, user):
        revert(f"Unauthorized user {user}", 1100)


class UnknownChainRevert:
    def __new__(cls, chain):
        revert(f"Unknown chain {chain}", 2000)


class RegisteredChainRevert:
    def __new__(cls, chain):
        revert(f"Registered chain {chain}", 2001)


class WrongChainRevert:
    def __new__(cls, cause):
        revert(f"Wrong chain: {cause} {2002}", 2002)


class UnknownTokenStandardRevert:
    def __new__(cls, standard):
        revert(f"Unknown token standard {standard}", 3000)


class RegisteredTokenStandardRevert:
    def __new__(cls, standard):
        revert(f"Registered token standard {standard}", 3001)


class UnauthorizedChainRevert:
    def __new__(cls, chain):
        revert(f"Unauthorized chain {chain}", 3002)


class RegisteredTokenRevert:
    def __new__(cls, token):
        revert(f"Registered token {token}", 3102)


class UnknownTokenAddressRevert:
    def __new__(cls, address):
        revert(f"Unknown token address {address}", 3101)


class OutOfBalanceRevert:
    def __new__(cls, _amount, balance):
        revert(f"Out of balance revert, requested {_amount} \n now balance: {balance}", 3200)


class UnknownTokenRevert:
    def __new__(cls, origin, name):
        revert(f"Unknown token {origin}, {name}", 3100)


class UnknownRequestTypeRevert:
    def __new__(cls, name):
        revert(f"Unknown request type: {name}", 4000)


class UnknownMessageTagRevert:
    def __new__(cls, tag):
        revert(f"Unknown tag {tag}", 4001)


class UnknownBalanceLabelRevert:
    def __new__(cls, label):
        revert(f"Unknown balance label: {label}", 3103)


class UnknownRequestRevert:
    def __new__(cls, request_id):
        revert(f"Unknown request id : {request_id}", 4002)


class DuplicatedRequestRevert:
    def __new__(cls, request_id):
        revert(f"Duplicated request : {request_id}", 4003)


class UnknownPendingRequestRevert:
    def __new__(cls, request_id):
        revert(f"Unknown pending request : {request_id}", 4004)
