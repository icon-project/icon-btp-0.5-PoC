# BTP Token Transfer Demo.

BTP를 활용하면 srcChain의 Token(IRC2)을 dstChain의 Intertoken으로 전송할 수 있다. 결과적으로 Token Contract의 user balace가 전송량만큼 감소하고 Intertoken의 balace그 전송량만큼 증가한다. 위 과정이 수행되기 위해서 각 체인에 BMC, Verifier Contract가 동작해야하며 srcChain에 Token Contract가, dstChain에는 Intertoken Contract가 동작해야한다. (총 Contracts 6개)


## BTP Management Contract

Blockchain에 등록된 BTP Management Contract(BMC)는 연결된 다른 체인과 Token의 정보를 갖고, 모든 BTP Message의 End Point 역할을 수행한다. BMC가 Token을 상대체인에 전송하기 위해서 사전에 상대체인에 대한 정보가 등록되어야 한다. 또한 상대 체인에서 처리된 Tx_receipt를 검증하는 Verifier Contract와 Token Contract가 BMC에 등록되어야 한다. 자세한 내용은 [BTP_Architecture_V0.5](docs/BTP_v0.5_Architecture.md)에 기술되어 있다.


### BMC Deployment
Blockchain에 BMC를 Deploy 할 때, Blockchain의 이름과 permission 값을 인자로 전달한다. permmision은 해당 체인으로 Tx 전송, Query, Token transfer에 대한 권한을 표현하는 String이다. (e.g., 000, 111, 101)
(자세한 내용은 [BlockchainManagement.md](docs/BMC/BlockchainManagement.md) 확인 가능하다.)

#### on_install

```python
def on_install(self, my_chain_name: str, my_chain_permission: str)
```

- my_chain_name : chain 이름
- my_chain_permission : Permission of the chain
TODO
BMC Deploy시 permission을 줄 필요 없이, 항상 111로 설정하도록 수정

 

#### Deploy Example

```python
transaction = DeployTransactionBuilder() \
            .from_("hx00123...") \
            .to("cx0000000000000000000000000000000000000000") \
            .step_limit(9999999999999) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content({ziped bmc}) \
            .params({"my_chain_name": "ICON",
                    "my_chain_permission": "111"}) \
            .build()
signed_tx = SignedTransaction(transaction, wallet) # iconsdk.wallet.wallet.KeyWallet
tx_hash = icon_service.send_transaction(signed_tx) # iconsdk.icon_service.IconService

```



### Register Chain

BMC에 상대 Blockchain을 연결하기 위해서는, 상대 블록체인에서 처리된 Tx_receipt를 검증할 수 있는 Verifier Contract의 주소와 상대 체인 정보글 등록해야 한다. Verifier Contract는 상대 체인의 Tx 처리 과정에 따라 알고리즘이 상이할 수 있다. 자세한 내용은 [Verifier Contract](docs/BMC/BlockchainManagement.md) 확인 할 수 있다.

#### registerChain

```python
@external
@only_owner
def registerChain(self, _name: str, _permission: str, _verifierAddr: Address, _description: str)
```

- _name: 연결하는 Chain의 이름
- _permission: 연결하는 Chain의 permission
- _verifierAddr: 연결하는 Chain의 Verifier Contract Address
- _description: 연결하는 Chain에 대한 description



#### Register Example

```python
transaction = CallTransactionBuilder() \
            .from_("hx00112321....")) \
            .to({BMCAddr}) \
            .step_limit(100000000000000) \
            .nid(3) \
            .nonce(2) \
            .method("registerChain") \
            .params({
              "_name": "dstChain",
              "_permission": "111",
              "_proverAddr": "cx012adf..."
              "_description": "other chain is eth like ... "
            }) \
            .build()
signed_tx = SignedTransaction(transaction, wallet) # iconsdk.wallet.wallet.KeyWallet
tx_hash = icon_service.send_transaction(signed_tx) # iconsdk.icon_service.IconService
```



### Register Token

BTP를 이용해서 Token을 보내고 받기 위해서는 사전에 BMC에 토큰을 등록하여야 한다. 기존 IRC2 Token이 상대 체인에서 생성되려면 대응하는 Intertoken Contract가 상대 체인에 deploy되어 있어야 한다. 이때, Original Token은 "Native Token", 상대체인에서의 Mirror Token은 "Non-Native Token" 또는 "Forign Token"으로 명명된다. 대응되는 Native Token과 Non-native Token은 같은 "Token Home"으로 묶이며, Token Home은 Native Token이 deploy된 Chain으로 정한다. 각 Token Contract는 해당 Chain의 BMC의 registerToken 메서드를 통해 등록한다.
자세한 내용은 [InterchainTokenSystem](docs/token_kr.md) 문서를 확인할 수 있다.


#### registerToken

```python
@external
def registerToken(self, _home: str, _standard: str, _name: str, _tokenContractAddr: Address):
```

- _home : Token Home Chain의 이름
- _standard : Token Standard (e.g., IRC2)
- _name : Token의 이름
- _tokenContractAddr: Token Contract의 주소




#### Register Example

```python
transaction = CallTransactionBuilder() \
            .from_(self._wallet.get_address()) \
            .to(self.contract_info[contract_name]) \
            .step_limit(100000000000000) \
            .nid(3) \
            .nonce(2) \
            .method("registerToken") \
            .params({
              "_home": "ICON",
              "_standard": "IRC2",
              "_name": "sample",
              "_tokenContractAddr": "cx01230dc...."
            }) \
            .build()
```


## Verifier Contract

Blockchain의 Verifier Contract는 상대체인에서 해당 BTP Msg가를 포함한 Transaction이 정상적으로 처리되었는지 검증한다. BTP Msg는 Relayer가 자신이 생성한 Proof of Existance 값과 함께 상대 체인으로 전달한다. Verifier는 전달 받은 poe 값으로 상대 체인의 Transaction을 검증한다.


### Deployment

예를 들어 A Chain의 Verifier Contract는 연결하려는 B Chain의 관리자가 구현하여 A Chain에 Deploy 한다. 한편, Verifier Contract의 검증 로직은 BMC가 호출하기 때문에 아래 함수 시그니쳐를 갖는 메서드를 포함해야한다. 아래 메서드는 tx_receipt을 검증하고 BTP Msg를 해석한다.

```python
    def prove_and_deserialize_message(self, tx_receipt: str, poe: str) -> dict:
```

- tx_receipt : 상대 체인에서 BTP Msg를 생성한 Transaction의 결과
- poe : tx_receipt의 정당성을 검증할 수 있는 Proof



## Token Contract

기존에 서비스 중이거나 새롭게 Deploy 될 IRC2 Token Contract는 소스코드 수정이나 표준 변경등의 작업 없이 BTP를 통해 다른 체인으로 토큰을 전송할 수 있다.


## Intertoken Contract

Intertoken Contract는 Non-native Token으로 활용될수 있다. 즉, 상대 체인에서 송신된 Token을 수신할 수 있다. 송신 Token과 수신 Token은 서로 다른 Chain에 Deploy된 Contract이므로 Balance 동기화가 되어 있지 않다. 따라서 BTP를 통한 Token Transfer가 발생할 경우 수신 Token은 수신량만큼 Token을 발행하여 수신자의 Balance에 더해주어야 한다. 결론적으로 Intertoken은 BMC에 의한 Mint 기능을 제공하는 Token이다.


### Minth Method

```python
def mint(self, _to: Address, _value: int, _data: bytes = None):
```

- _to : BTP를 통한 Token Transfer의 수신인 주소
- _value : Token 전송량
- _data : None

















