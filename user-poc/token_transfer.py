#!/usr/bin/env python
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

from ICONServiceManager.chain_manager import ChainManager
from ICONServiceManager.balancetable import BalanceTable
from iconsdk.wallet.wallet import KeyWallet

DEFAULT_SRC_CONFIG_PATH = "../contract-poc/out/src_chain_info.json"
DEFAULT_DST_CONFIG_PATH = "../contract-poc/out/dst_chain_info.json"
S_WALLET_PATH = "./config/wallets/__________________________SENDER.wallet"
R_WALLET_PATH = "./config/wallets/________________________RECIEVER.wallet"

src_chain = ChainManager(DEFAULT_SRC_CONFIG_PATH, S_WALLET_PATH, "test")
dst_chain = ChainManager(DEFAULT_DST_CONFIG_PATH, R_WALLET_PATH, "test")

bt = BalanceTable(src_chain, dst_chain)

# 0. balances check
print("<Scenario 1 : Token Transfer>")
bt.print_table()

# 1. Request token to faucet
tx_result = src_chain.call_tx(src_chain.token, "faucet", {})
src_chain.print_result(tx_result)
bt.print_table()

# 2. Deposit
print("[Sender] Step 1. \"Deposit\" Tx -> \"A_Token(srcChain)\", send it?")
tx_result = src_chain.call_tx(src_chain.token, "transfer", params={"_to": src_chain.bmc, "_value": 500})
src_chain.print_result(tx_result)
bt.print_table()

# 2. SendToken(BTP Request)
print("[Sender] Step 2. \"sendToken\" Tx -> BMC(srcChain), send it?")

params = {
    "to_chain": dst_chain.chain_name,
    "token_home": src_chain._score_info["token"]["info"]["token_home"],
    "token_name": src_chain._score_info["token"]["info"]["token_name"],
    "to_eoa": "hxf4f30e425a067eb6dd00e0a6f467b60c24193eb2",  # account in Chain B
    "amount": 200
}
# src_chain.dummy_tx_send(10)
tx_result = src_chain.call_tx(src_chain.bmc, "sendToken", params)
src_chain.print_result(tx_result)
bt.print_table()

break_ = True
while break_:
    demo = input("[Sender] print balance table? [yn]")
    if demo == "y":
        bt.print_table()
    else:
        break_ = False



