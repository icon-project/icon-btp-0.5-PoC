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
# Message manager of BMC.
# When client requests btp-request to the BMC, message manager generates btp msg.

from iconservice import *

from .btp_message import BTPMsg
from ..bases.reverts import *
from ..chain_manager.chain_manager import ChainManager
from ..token_manager.token_manager import TokenManager
from ..interfaces.foreignertoken import ForeignerToken
from ..interfaces.irc2 import Irc2


class MessageManager:
    def __init__(self, db: IconScoreDatabase, chain_manager: ChainManager, token_manager: TokenManager, bmc):

        self._db = db
        self._pending_request_db = DictDB("pending_requests", db, str)  # key: request ID
        self._request_status = DictDB("request_status", db, str)  # key: request ID
        self._chain_manager = chain_manager
        self._token_manager = token_manager
        self._bmc = bmc

    def send_token(self, to_chain: str, token_home: str, token_name: str, to_eoa: Address, amount: int):

        bmc_home = self._chain_manager.get_bmc_home()
        if bmc_home == to_chain:
            WrongChainRevert("BTP Message can't send self chain")

        # check destination if the chain is registered or not
        try:
            self._chain_manager.get_chain_info(to_chain)
        except KeyError:
            UnknownChainRevert(to_chain)

        # Generates BTP Request
        request_msg = BTPMsg()
        from_chain = self._chain_manager.get_bmc_home()
        from_eoa = self._bmc.msg.sender
        request_id = f"{from_chain}#{self._bmc.tx.hash.hex()}"

        request_msg.build_branch("base", status="Request", msg_type="Transfer", request_id=request_id)
        request_msg.build_branch("from", chain=self._chain_manager.get_bmc_home(), account=from_eoa)
        request_msg.build_branch("to", chain=to_chain)
        request_msg.build_branch("token", home=token_home, name=token_name, to_eoa=to_eoa, amount=amount)
        # TODO timeout branch

        bank = self._token_manager.get_bank()
        # Lock Token to be sent.
        if not bank.lockToken(token_home, token_name, from_eoa, amount):
            OutOfBalanceRevert(amount, self._token_manager.get_balance(token_home, token_name, from_eoa, "balance"))
        # emit event log.
        self._bmc.SendToken(token_home, token_name, to_chain, to_eoa, amount)

        # register btp-msg to the BMC
        btp_msg = self._register_request(request_msg)

        # record btp-msg in order to be read by relayers
        self._bmc.Message(btp_msg)

    def relay_message(self, from_chain: str, poe: str):

        try:
            verifier = self._chain_manager.get_verifier(from_chain)
        except IconScoreException as error:
            UnknownChainRevert(error)

        # Let verifier score verify the btp request msg
        msg = verifier.verify_btp_msg(poe)
        btp_msg = BTPMsg()
        btp_msg.from_string(msg)

        if not self._chain_manager.is_home(btp_msg.to_.chain):
            revert("wrong direction msg")

        if btp_msg.base_.status == "Request":
            self._process_request(btp_msg)
        elif btp_msg.base_.status == "Commit":
            self._process_commit(btp_msg)
        else:
            UnknownMessageTagRevert(btp_msg.base_.status)

    def _register_request(self, msg: BTPMsg):
        request_id = msg.base_.request_id
        self._request_status[request_id] = "Pending"
        btp_msg = msg.to_json()
        self._pending_request_db[request_id] = btp_msg
        return btp_msg

    def _process_request(self, btp_msg: BTPMsg):
        request_msg = btp_msg

        # Prevention for Double Process Attack
        if self._request_status[request_msg.base_.request_id]:
            DuplicatedRequestRevert(request_msg.base_.request_id)

        commit_msg = BTPMsg()

        if request_msg.base_.msg_type == "Transfer":
            token_addr = self._token_manager.get_token_addr(request_msg.token_.home, request_msg.token_.name)
            if not self._chain_manager.is_home(request_msg.token_.home):
                token_score = self._bmc.create_interface_score(token_addr, ForeignerToken)
                result = token_score.mint(request_msg.token_.to_eoa, request_msg.token_.amount)
            else:
                token_score = self._bmc.create_interface_score(token_addr, Irc2)
                result = token_score.transfer(request_msg.token_.to_eoa, request_msg.token_.amount)
        else:
            # TODO: Case of msg_type == Transaction
            result = True

        # Generates btp-msg for commit
        commit_msg.base_ = request_msg.base_
        commit_msg.base_.status = "Commit"

        commit_msg.from_.chain = request_msg.to_.chain
        commit_msg.to_.chain = request_msg.from_.chain

        commit_msg.build_branch("receipt", valid=True, result=result, code=1, msg="ok")
        # TODO timeout branch
        str_msg = commit_msg.to_json()

        # register btp-msg to the BMC
        self._request_status[commit_msg.base_.request_id] = "Completed"

        # record btp-msg in order to be read by relayers
        self._bmc.Message(str_msg)

    def _process_commit(self, commit_msg: BTPMsg):

        request_msg = BTPMsg()

        status = self.get_request_status(commit_msg.base_.request_id)
        if not status:
            UnknownRequestRevert(commit_msg.base_.request_id)
        if status == "Completed":
            revert("The request already was complete ")
        else:
            request_str = self.get_pending_request(commit_msg.base_.request_id)
            request_msg.from_string(request_str)

        if request_msg.base_.msg_type == "Transfer":
            bank = self._token_manager.get_bank()
            token_home = request_msg.token_.home
            token_name = request_msg.token_.name
            from_account = request_msg.from_.account
            amount = request_msg.token_.amount

            if commit_msg.receipt_.valid:
                # Unlock token(when sendToken succeeded)
                if not bank.unlockToken(token_home, token_name, from_account, amount):
                    balance = self._token_manager.get_balance(token_home, token_name, from_account, "locked_balance")
                    OutOfBalanceRevert(amount, balance)
            else:
                # Roll back token(when sendToken failed)
                if not bank.rollBack(token_home, token_name, from_account, amount):
                    balance = self._token_manager.get_balance(token_home, token_name, from_account, "balance")
                    OutOfBalanceRevert(amount, balance)
        else:
            # TODO request_msg.base_.msg_type == "Transaction"
            pass

        self._request_status[request_msg.base_.request_id] = "Completed"

    def get_request_status(self, request_id: str) -> str:
        status = self._request_status[request_id]
        if not status:
            return ""
        return status

    def get_pending_request(self, request_id: str) -> str:
        return self._pending_request_db[request_id]

    def rm_pending_request(self, request_id: str) -> bool:

        if self._pending_request_db[request_id]:
            del self._pending_request_db[request_id]
            return True
        else:
            return False
