# BTP SCORE Deployer
BTP SCORE Deployer is a program to deploy BTP Contracts on *SrcChain* and *dstChain*. So, this program requires information about each node of blockchain and all of scores to be deployed.

## Configuration
This program starts with config files located at "/contract-poc/deploy_config/".

file_name|description
---------|-----------
dst_node_config.json|Info. of node of *DstChain*
src_node_config.json|Info. of node of *SrcChain*
dst_score_config.json|Info. of scores on *DstChain*
src_score_config.json|Info. of scores on *SrcChain*


### node_config.json
Both of "node_config.json" coressponding loopchains include the following keys and values

#### Example
```bash
{
  "chain_name": "DstChain",
  "nid": 0x4,
  "web_protocol": "http", # or "ssl" 
  "address": "localhsot:9100"
}
```
### score_config.json
Both of "score_config.json" coressponding loopchains include the following keys and values

#### Example
```bash
{
  "BMC": {
    "path":"../contracts/btp_management_contract/",
    "info": "",
    "install_params": {
      "my_chain_name": "DstChain"
    }
  },
  "verifier": {
    "path": "../contracts/icon_verifier",
    "info": {
      "home_chain": "SrcChain"
    },
    "install_params": {
      "packed_rep_list": "hx615724e1bf1c4db4c9acf4c0b2c584505de9ad9c"
    }
  },
  "token": {
    "path": "../contracts/foreigner_token",
    "info": {
      "token_home": "SrcChain",
      "token_name": "BTP_Token",
      "std_name": "IRC2"
    },
    "install_params" : {}
  }
}
```

## Install
```bash
$ cd contract-poc
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirement
```

## Run
This program sends 6 deployment transactions and 5 call transactions to loopchains. So, two loopchains should run before this program works.
```bash
$ source venv/bin/activate
$ cd contract-poc/deploy_src
$ ./BTP_score_deploy.py
```

## Output file
The deployer generates output files, named dst_chain_info.json and src_chain_info.json, which is used to configurate *Relayers* and *users*. They should learn addresses of scores deployed in above step and node information to send transactions.

#### Example: chain_info.json
```bash
{
    "address": "localhost:9100",
    "chain_name": "DstChain",
    "channel": "icon_dex",
    "nid": "0x4",
    "scores": {
        "BMC": {
            "deploy_txHash": "0xfcd4c98dc2860eaa0a8da2ee6282c95b7e00bccbf165f58ff9edaf063d9c42bd",
            "info": "",
            "score_addr": "cx98fe5dc552cd60abc0b0cffd177dfa436822faf1"
        },
        "token": {
            "deploy_txHash": "0x86218469cb633ef1340ddbda40415afe6bf247c76f45182faaefc9c89cda8002",
            "info": {
                "std_name": "IRC2",
                "token_home": "SrcChain",
                "token_name": "BTP_Token"
            },
            "score_addr": "cx6dabffa1255fa55835b0e954350dd3b2daa23ccf"
        },
        "verifier": {
            "deploy_txHash": "0x731d07f0ccd0c302b3c1ad9430011e473f65dd179779151624f16bced1da2d6d",
            "info": {
                "home_chain": "SrcChain"
            },
            "score_addr": "cx434812e46ea25ffc1e8964de6eb215e4f29eb9e5"
        }
    },
    "web_protocol": "http"
}
```



