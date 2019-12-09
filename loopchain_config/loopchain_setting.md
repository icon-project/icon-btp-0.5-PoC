# Loopchain Install and Run


## Loopchain Node Install

### Loopchain Build
Install the *Requirement* specified in the [loopchain repository](https://github.com/icon-project/loopchain) and build loopchain. Note that the initial settings used in the PoC project are based on tag 2.4.19 of loopchain.


##### LoopChain Biuld
We downloads loopchain source code and build it for BTP PoC in the below commands. However, manual in loopchain repository is recommended.
```bash
$ git clone https://github.com/icon-project/loopchain.git LoopChain
$ cd LoopChain
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirement.txt
$ git checkout 2.4.19
$ make all
```

## Loopchain Configuration
Run two Loopchains with different configurations with a copy of loopchain source code. Thus, we provides config files for each loopchains. just copy them like below command.
```bash

$ cp -rf [BTP0.5-PoC_ROOT]/loopchain_config [LoopChain_ROOT]/

```

## Running Loopchain nodes

##### Run *SrcChain* node
```bash
$ cd [LoopChain_ROOT]
$ loop peer -o loopchain_config/src_node_config/node_conf.json
```
##### Run *DstChain* node 실행
```bash
$ cd [LoopChain_ROOT]
$ loop peer -o loopchain_config/dst_node_config/node_conf.json
```

## Configuration File Information

#### For Blockchain.

File|description
----|-----------
init_genesis_test.json|initial network information(e.g. nid, initial account)
channel_manage_data.json| List of Nodes participating concensus.

#### For a Node

File|description
----|-----------
node_conf.json|Channel_manage_data file path, kestore file path for node key, node's info.
keyStoreFile|Node key used of consensus.

