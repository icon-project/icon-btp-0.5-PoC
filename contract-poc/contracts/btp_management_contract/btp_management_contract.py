#
#
# BMC(BTP Management Contract)
# BTP is an interchain protocol performed between BMCs deployed in two blockchains. the BMC, the system contract,
# is responsible for creating, sending, receiving and processing these BTP messages. Therefore, it manages
# the information about the connected blockchain and the token to be transmitted and has a method designed
# to interact with the relayer.


from iconservice import *

from .chain_manager.chain_manager import ChainManager
from .message_manager.message_manager import MessageManager
from .token_manager.token_manager import TokenManager


class BtpManagementContract(IconScoreBase):
    @eventlog
    def RegisterChain(self, chain_name: str, verifier_addr: Address, description: str):
        pass

    @eventlog
    def RegisterToken(self, token_home: str, token_name: str, standard: str, token_score_addr: Address):
        pass

    @eventlog
    def SendToken(self, token_home: str, token_name: str, to_chain: str, to_eoa: Address, amount: int):
        pass

    @eventlog
    def Deposit(self, token_home: str, token_name: str, from_eoa: Address, amount: int):
        pass

    @eventlog
    def Burn(self, token_home: str, token_name: str, target_eoa: Address, amount: int):
        pass

    @eventlog
    def LockToken(self, token_home: str, token_name: str, target_eoa: Address, amount: int):
        pass

    def UnLockToken(self, token_home: str, token_name: str, target_eoa: Address, amount: int):
        pass

    @eventlog
    def Withdraw(self, token_home: str, token_name: str, target_eoa: Address, amount: int):
        pass

    @eventlog
    def Message(self, btp_msg: str):  # TODO btp_msg의 자료형은?
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._chain_manager = ChainManager(db, self)
        self._token_manager = TokenManager(db, self._chain_manager, self)
        self._message_manager = MessageManager(db, self._chain_manager, self._token_manager, self)

    def on_install(self, my_chain_name: str) -> None:
        super().on_install()
        self._chain_manager.set_my_chain(my_chain_name)
        self._token_manager.register_standard("IRC2", "temp_params")
        # TODO supports additional token standard

    def on_update(self) -> None:
        super().on_update()

    @payable
    def fallback(self):
        """ Called when the BMC receives icx via icx_transfer, then deposits icx as a token."""
        self._token_manager.deposit(self.msg.sender, self.msg.value, None)
        # self.Deposit("ICON", "ICX", self.msg.sender, self.msg.value)

    @external
    def tokenFallback(self, from_eoa: Address, amount: int, data: bytes = None):
        """ Called by token contract, when a client send token to the BMC. then deposits token."""
        print("In token fallback of bmc")
        print("from_eoa:", from_eoa)
        print("amount: ", amount)
        self._token_manager.deposit(from_eoa, amount, self.msg.sender)

    @external
    def registerChain(self, chain_name: str, verifier_addr: Address, description: str):
        """ Registers chain to be connect."""

        self._chain_manager.register(chain_name, verifier_addr, description)
        self.RegisterChain(chain_name, verifier_addr, description)

    @external
    def registerToken(self, token_home: str, token_name: str, std_name: str, token_score_addr: Address):
        """ Registers token contract to be sent. """

        self._token_manager.register_token(token_home, token_name, std_name, token_score_addr)

    @external(readonly=True)
    def getBalance(self, token_home: str, token_name: str, target_eoa: Address) -> int:
        return self._token_manager.get_balance(token_home, token_name, target_eoa, "")

    @external(readonly=True)
    def getLockedBalance(self, token_home: str, token_name: str, target_eoa: Address) -> int:
        return self._token_manager.get_balance(token_home, token_name, target_eoa, "locked")

    @external(readonly=True)
    def getTokenAddr(self, token_home: str, token_name: str) -> Address:
        return self._token_manager.get_token_addr(token_home, token_name)

    @external(readonly=True)
    def getChainInfo(self, chain_name: str) -> str:
        return str(self._chain_manager.get_chain_info(chain_name))

    # TODO
    # @external
    # def timeout_rollBack(self, request_id: str):
    #     self._message_manager.timeout_rollback(request_id, self.tx.timestamp)
    #     pass

    @external
    def withdraw(self, token_home: str, token_name: str, amount: int):
        self._token_manager.withdraw(token_home, token_name, self.msg.sender, amount)

    @external
    def sendToken(self, to_chain: str, token_home: str, token_name: str, to_eoa: Address, amount: int):
        """ generates btp-msg which means a client wants to send token to one of another chain. """
        self._message_manager.send_token(to_chain, token_home, token_name, to_eoa, amount)

    @external  # BMC의 받기 기능 srcChain에 BTP msg가 생성되면, relayer가 dstChain의 relayMessage함수를 호출함
    def relayMessage(self, from_chain: str, packed_poe: str):
        """ When relayer detects btp-msg, it relays msg via this method."""
        self._message_manager.relay_message(from_chain, packed_poe)


