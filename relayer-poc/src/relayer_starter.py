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
import asyncio
import argparse
from icon_relayer import IconRelayer

DEFAULT_SRC_CONFIG_PATH = "../../contract-poc/out/src_chain_info.json"
DEFAULT_DST_CONFIG_PATH = "../../contract-poc/out/dst_chain_info.json"


class UnknownChainType(Exception):
    pass


async def rep_main():
    args = _init_parser()

    if args.direction == "forward":
        read_chain_path = DEFAULT_SRC_CONFIG_PATH
        write_chain_path = DEFAULT_DST_CONFIG_PATH
    elif args.direction == "backward":
        read_chain_path = DEFAULT_DST_CONFIG_PATH
        write_chain_path= DEFAULT_SRC_CONFIG_PATH

    relayer = IconRelayer(read_chain_path, write_chain_path)

    await relayer.start()


def _init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--direction", help="\"direction\" of the relayer, forward or backward")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rep_main())
