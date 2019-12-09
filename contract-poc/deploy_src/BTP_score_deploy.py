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
import os
import sys
import json
import shutil
from time import sleep

from iconsdk.builder.transaction_builder import DeployTransactionBuilder, CallTransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

SRC_NODE_CONFIG_PATH = "../deploy_configs/src_node_config.json"
SRC_SCORE_CONFIG_PATH = "../deploy_configs/src_score_config.json"
DST_NODE_CONFIG_PATH = "../deploy_configs/dst_node_config.json"
DST_SCORE_CONFIG_PATH = "../deploy_configs/dst_score_config.json"

CREATOR_WALLET_PATH = "../deploy_configs/wallets/_________________________CREATOR.wallet"
PASSWD = "test"

STEP_LIMIT = 10000000000
NONCE = 100
SLEEP_TIMER = 5


class UnknownOption(Exception):
    pass


class InvalidAddress(Exception):
    pass


class Deployer:

    def __init__(self, node_conf_path: str, wallet_path: str, passwd: str):

        # Node configuration to be connected
        with open(node_conf_path, "r") as f:
            node_conf = json.load(f)

        self._my_chain_name = node_conf["chain_name"]
        self._nid = int(node_conf["nid"], 16)

        if node_conf["web_protocol"] == "ssl":
            self._icon_service = IconService(HTTPProvider("https://"+node_conf["address"], 3))
        else:
            self._icon_service = IconService(HTTPProvider("http://"+node_conf["address"], 3))
        print(f"--------------------------------<Connecting node>--------------------------------")
        print(f" - address    : {node_conf['address']}")
        print(f" - chain_name : {self._my_chain_name}")
        print(f" - nid        : {self._nid}")
        print(f"---------------------------------------------------------------------------------")

        # Set wallet of deployer
        self._wallet = KeyWallet.load(wallet_path, passwd)
        # print(f"pk: {self._wallet.get_private_key()}")

        # Set deployed score address
        self._score_addr = ""  # It will be set after deployment
        self._score_path = ""
        self._score_params = {}
        self._score_info = ""

    def deploy_score(self) -> dict:
        tx_result = self._deploy_score(self._score_path, self._score_params)
        try:
            self._score_addr = tx_result["scoreAddress"]
        except KeyError:
            sys.exit()

        return {
            "deploy_txHash": tx_result["txHash"],
            "score_addr": self._score_addr,
            "info": self._score_info
        }

    def _deploy_score(self, score_path: str, params: dict) -> dict:

        # Make zipfile of a score
        # score_content = gen_deploy_data_content(score_path)

        shutil.make_archive("./tmp", "zip", score_path)
        with open("./tmp.zip", "rb") as z:
            score_content = z.read()
        os.remove("./tmp.zip")

        transaction = DeployTransactionBuilder() \
            .from_(self._wallet.get_address()) \
            .to("cx0000000000000000000000000000000000000000") \
            .step_limit(STEP_LIMIT) \
            .nid(self._nid) \
            .nonce(NONCE) \
            .content_type("application/zip") \
            .content(score_content) \
            .params(params) \
            .build()

        return self._send_transaction(transaction)

    def _call_tx(self, score_addr: str, method: str, params: dict) -> dict:

        transaction = CallTransactionBuilder() \
            .from_(self._wallet.get_address()) \
            .to(score_addr) \
            .step_limit(STEP_LIMIT) \
            .nid(self._nid) \
            .nonce(NONCE) \
            .method(method) \
            .params(params) \
            .build()
        return self._send_transaction(transaction)

    def _send_transaction(self, transaction):
        signed_tx = SignedTransaction(transaction, self._wallet)
        tx_hash = self._icon_service.send_transaction(signed_tx)

        sleep(SLEEP_TIMER)
        tx_result = self._icon_service.get_transaction_result(tx_hash)

        self.print_result(tx_result)
        return tx_result

    @property
    def score_addr(self):
        return self._score_addr

    @score_addr.setter
    def score_addr(self, my_addr):
        self._score_addr = my_addr

    @staticmethod
    def print_result(data: dict):
        print("-----------------------------------<Tx_result>-----------------------------------")
        print(f" -    txHash: {data['txHash']}")
        print(f" -    height: {data['blockHeight']}")
        try:
            print(f" -   failure: {data['failure']['code']}.{data['failure']['message']}")
            print(f" - scoreAddr: {data['scoreAddress']}")
        except KeyError:
            pass

        print(f" -  stepUsed: {data['stepUsed']}")
        print(f" -    status: {data['status']}")
        print("---------------------------------------------------------------------------------\n\n")


class BMCDeployer(Deployer):

    def __init__(self, node_conf_path: str, score_conf_path: str, wallet_path: str, passwd: str):
        super().__init__(node_conf_path, wallet_path, passwd)

        with open(score_conf_path, "r") as f:
            self._score_conf = json.load(f)

        self._score_path = self._score_conf["BMC"]["path"]
        self._score_params = self._score_conf["BMC"]["install_params"]
        self._score_info = self._score_conf["BMC"]["info"]

    def register_verifier(self, verifier_info: dict):

        if not self._score_addr:
            raise InvalidAddress

        verifier_addr = verifier_info["score_addr"]
        home_chain = verifier_info["info"]["home_chain"]

        self._call_tx(
            score_addr=self._score_addr,
            method="registerChain",
            params={
                "chain_name": home_chain,
                "verifier_addr": verifier_addr,
                "description": ""
            })

    def register_token(self, token_info: dict):

        if not self._score_addr:
            raise InvalidAddress

        token_addr = token_info["score_addr"]
        home = token_info["info"]["token_home"]
        name = token_info["info"]["token_name"]
        std = token_info["info"]["std_name"]

        self._call_tx(
            score_addr=self._score_addr,
            method="registerToken",
            params={
                "token_home": home,
                "token_name": name,
                "std_name": std,
                "token_score_addr": token_addr
            }
        )


class VerifierDeployer(Deployer):

    def __init__(self, node_conf_path: str, score_conf_path: str, wallet_path: str, passwd: str):
        super().__init__(node_conf_path, wallet_path, passwd)

        with open(score_conf_path, "r") as f:
            self._score_conf = json.load(f)

        self._score_path = self._score_conf["verifier"]["path"]
        self._score_params = self._score_conf["verifier"]["install_params"]
        self._score_info = self._score_conf["verifier"]["info"]


class TokenDeployer(Deployer):

    def __init__(self, node_conf_path: str, score_conf_path: str, wallet_path: str, passwd: str):
        super().__init__(node_conf_path, wallet_path, passwd)

        with open(score_conf_path, "r") as f:
            self._score_conf = json.load(f)

        self._score_path = self._score_conf["token"]["path"]
        self._score_params = self._score_conf["token"]["install_params"]
        self._score_info = self._score_conf["token"]["info"]

    def set_bmc_addr(self, bmc_addr: str):

        if not self._score_addr:
            raise InvalidAddress

        self._call_tx(
            score_addr=self._score_addr,
            method="set_bmc",
            params={
                "bmc_addr": bmc_addr
            })


def print_info(title: str, data: dict):
    print("---------------------------------<", title, ">----------------------------------")
    json_string = json.dumps(data, indent=4)
    print(json_string)
    print("---------------------------------------------------------------------------------\n\n")


def deploy_btp_scores(node_conf_path: str, score_conf_path: str) -> dict:

    score_info = {}

    print("[Deploy] BMC")
    bmc = BMCDeployer(node_conf_path, score_conf_path, CREATOR_WALLET_PATH, PASSWD)
    score_info["BMC"] = bmc.deploy_score()

    print("[Deploy] Verifier")
    verifier = VerifierDeployer(node_conf_path, score_conf_path, CREATOR_WALLET_PATH, PASSWD)
    score_info["verifier"] = verifier.deploy_score()

    print("[Deploy] Token SCORE")
    token = TokenDeployer(node_conf_path, score_conf_path, CREATOR_WALLET_PATH, PASSWD)
    score_info["token"] = token.deploy_score()

    with open(node_conf_path, "r") as f:
        node_conf = json.load(f)

    return {
        "web_protocol": node_conf["web_protocol"],
        "address": node_conf["address"],
        "chain_name": node_conf["chain_name"],
        "channel": "icon_dex",
        "nid": node_conf["nid"],
        "scores": {
            "token": score_info["token"],
            "BMC": score_info["BMC"],
            "verifier": score_info["verifier"]
        }
    }


def deploy():
    src_chain_info = deploy_btp_scores(SRC_NODE_CONFIG_PATH, SRC_SCORE_CONFIG_PATH)
    dst_chain_info = deploy_btp_scores(DST_NODE_CONFIG_PATH, DST_SCORE_CONFIG_PATH)

    if not os.path.isdir("../out"):
        os.mkdir("../out")

    with open("../out/src_chain_info.json", "w") as f:
        json.dump(src_chain_info, fp=f, sort_keys=True, indent=4)

    with open("../out/dst_chain_info.json", "w") as f:
        json.dump(dst_chain_info, fp=f, sort_keys=True, indent=4)

    src_bmc = BMCDeployer(SRC_NODE_CONFIG_PATH, SRC_SCORE_CONFIG_PATH, CREATOR_WALLET_PATH, PASSWD)
    src_bmc.score_addr = src_chain_info["scores"]["BMC"]["score_addr"]

    print("[CallBMC] Register Chain")
    src_bmc.register_verifier(src_chain_info["scores"]["verifier"])
    print("[CallBMC] Register Token")
    src_bmc.register_token(src_chain_info["scores"]["token"])

    dst_bmc = BMCDeployer(DST_NODE_CONFIG_PATH, DST_SCORE_CONFIG_PATH, CREATOR_WALLET_PATH, PASSWD)
    dst_bmc.score_addr = dst_chain_info["scores"]["BMC"]["score_addr"]

    print("[CallBMC] Register Chain")
    dst_bmc.register_verifier(dst_chain_info["scores"]["verifier"])
    print("[CallBMC] Register Token")
    dst_bmc.register_token(dst_chain_info["scores"]["token"])

    dst_token = TokenDeployer(DST_NODE_CONFIG_PATH, DST_SCORE_CONFIG_PATH, CREATOR_WALLET_PATH, PASSWD)
    dst_token.score_addr = dst_chain_info["scores"]["token"]["score_addr"]
    print("[CallToken] Register BMC")
    dst_token.set_bmc_addr(dst_chain_info["scores"]["BMC"]["score_addr"])


if __name__ == "__main__":
    deploy()
