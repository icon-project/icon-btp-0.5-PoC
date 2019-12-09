# Relayer

The Relayers monitors read-chain to check wheather new BTP message is generated. If it is detected, the Relayer generates proof of existance value. The PoE value claims that the BTP message exists on the blockchain. And then, the PoE including BTP message is sent to write-chain.  
There are 2 types of Relayer, difference between them is only configuration. Forward Relayer sets SrcChain to read-chain and Dstchain to write-chain, Backward Relayer sets in reverse. It means that both of Relayers standing different direction are requeired.  
 
## Relayer Configuration
*Relayer* is required configuration files, *src_chain_info.json* and *dst_chain_info.json*, which include node information and addresses of BTP scores. The configuration file has the following format. If you run deployer program we provide, this program refers to contract-poc/out by default. 

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
## Relayer Install

```bash
$ cd relayer-poc
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirement.txt
```

## Run
Two unidirectional *Relayers* should be worked for BTP communication, so that run this program with different options as following.

```bash
cd relayer-poc/src
$ ./relayer_starter.py -d "forward"  # read-chain: SrcChain, write-chain: DstChain

# or
cd relayer-poc/src
$ ./relayer_starter.py -d "backward"  # read-chain: DstChain, write-chain: SrcChain
```