from .chain_manager import ChainManager


class BalanceTable:
    def __init__(self, src_chain: ChainManager, dst_chain: ChainManager):
        self._sc = src_chain
        self._dc = dst_chain
        self._from_account = src_chain._wallet.get_address()
        self._to_account = dst_chain._wallet.get_address()

    def print_table(self):
        sb = self.get_token_balance(self._sc, self._from_account)
        sd = self.get_deposit(self._sc, self._from_account)
        sld = self.get_locked_deposit(self._sc, self._from_account)

        rb = self.get_token_balance(self._dc, self._to_account)
        rd = self.get_deposit(self._dc, self._to_account)
        rld = self.get_locked_deposit(self._dc, self._to_account)

        print(f"{'Balance Table':=^43}")
        print(f"-------------------------------------------")
        print(f"|        |   deposit|    locked|     token|")
        print(f"-------------------------------------------")
        print(f"|  sender|{int(sd, 16):>10}|{int(sld, 16):>10}|{int(sb, 16):>10}|")
        print(f"|receiver|{int(rd, 16):>10}|{int(rld, 16):>10}|{int(rb, 16):>10}|")
        print(f"-------------------------------------------\n")

    def get_token_balance(self, to_chain: ChainManager, owner: str) -> int:
        return to_chain.query(to_chain.token, "balanceOf", params={"_owner": owner})

    def get_deposit(self, to_chain: ChainManager, owner: str) -> int:

        params = {
            "token_home": to_chain._score_info["token"]["info"]["token_home"],
            "token_name": to_chain._score_info["token"]["info"]["token_name"],
            "target_eoa": owner
        }
        resp = to_chain.query(to_chain.bmc, "getBalance", params)
        return resp

    def get_locked_deposit(self, to_chain: ChainManager, owner: str) -> int:
        params = {
            "token_home": to_chain._score_info["token"]["info"]["token_home"],
            "token_name": to_chain._score_info["token"]["info"]["token_name"],
            "target_eoa": owner
        }
        return to_chain.query(to_chain.bmc, "getLockedBalance", params)

