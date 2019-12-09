# User's Behavior

In this PoC, *user A* on *SrcChain* want to transfer tokens to *user B* on *DstChain*. Thus he/she sends 3 transactions as following.  
1. Request 10,000 tokens to faucet function of token score on *SrcChain*.
2. Deposit 500 tokens to BMC
3. Send 200 tokens to *user B* on *DstChain*.

After first transaction is complete, *user A* get 100,000 tokens in the token score. And second transaction reduces user's balance on the token score by 500 and deposits 500 tokens to BMC. Finally, the last transaction converts 200 tokens of *user A*'s deposit on BMC to locked deposit. When 200 tokens mint to *user B* in token score on *DstChain*, the locked depoist become zero (lock released).  


## User Configuration
A client on *SrcChain* is required "src_chain_info.json" as a configuration file, which include node information and addresses of BTP scores. The configuration file has the following format. If you run deployer program we provide, this program refers to contract-poc/out by default.

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
## User Install
```bash
$ cd user-poc
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirement.txt
```

## Run
Two *Loopchains* and two *relayers* should work before running this program.
```bash
$ cd user-poc
$ source venv/bin/activate
$ ./token_transfer.py
```
