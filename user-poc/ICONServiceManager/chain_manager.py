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
from .service_manager import ServiceManager


class ChainManager(ServiceManager):
    def __init__(self, node_conf_path: str, wallet_path, passwd: str):
        super().__init__(node_conf_path, wallet_path, passwd)
        self._bmc_addr = self._score_info["BMC"]["score_addr"]
        self._verifier_addr = self._score_info["verifier"]["score_addr"]
        self._token_addr = self._score_info["token"]["score_addr"]

    @property
    def bmc(self):
        return self._bmc_addr

    @property
    def verifier(self):
        return self._verifier_addr

    @property
    def token(self):
        return self._token_addr

