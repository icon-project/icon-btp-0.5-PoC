#
#
# BTP message structure.
# BTP msg is dictionary format and consists of 4 branches of dict.
# BTP msg = {
#  baseBranch: {...},
#  FromBranch: {...},
#  ToBranch: {...},
#  TokenBranch: {...},
#  ReceiptBranch: {...},
#  etc: {...}
# }
#


from iconservice import json_dumps, json_loads
from ..bases.json_object import Attribute, AddressAttr, DictAttr, IntAttr, BoolAttr, JsonObject


class Branch:
    def __init__(self, name):
        self.branch_name = name
        self._init = False

    def to_dict(self):
        ret = self.__dict__.copy()
        ret.pop("branch_name")
        ret.pop("_init")
        return ret

    @property
    def init(self) -> bool:
        return self._init

    @init.setter
    def init(self, value: bool):
        self._init = value


class BaseBranch(Branch):
    status = Attribute("status")
    msg_type = Attribute("msg_type")
    request_id = Attribute("request_id")


class FromBranch(Branch):
    chain = Attribute("chain")
    account = AddressAttr("account")


class ToBranch(Branch):
    chain = Attribute("chain")
    contract = AddressAttr("contract")
    method = Attribute("method")
    params = DictAttr("params")


class TokenBranch(Branch):
    home = Attribute("home")
    name = Attribute("name")
    to_eoa = AddressAttr("to_eoa")
    amount = IntAttr("amount")


class ReceiptBranch(Branch):
    valid = BoolAttr("valid")
    result = DictAttr("result")
    code = IntAttr("code")
    msg = Attribute("msg")


class BTPMsg(JsonObject):

    def __init__(self):
        super().__init__()
        self.base_ = BaseBranch("base")
        self.from_ = FromBranch("from")
        self.to_ = ToBranch("to")
        self.token_ = TokenBranch("token")
        self.receipt_ = ReceiptBranch("receipt")

    @property
    def attributes(self):
        return self._attributes

    def build_branch(self, branch_name: str, **kwargs):
        obj = getattr(self, branch_name + "_", False)
        if obj:
            branch_dict = dict()
            for key, value in kwargs.items():
                setattr(obj, key, value)
                branch_dict[key] = value
            name = obj.branch_name
            self.attributes[name] = branch_dict

    def to_json(self):
        for branch_name in self.__dict__.keys():
            obj = getattr(self, branch_name, False)
            if getattr(obj, "_init", 0):
                branch_dict = dict()
                for key, value in obj.__dict__.items():
                    if key == "branch_name" or key == "_init":
                        continue
                    branch_dict[key[1:]] = value
                name = obj.branch_name
                self.attributes[name] = branch_dict

        json_root = dict()
        for branch_name in self.attributes.keys():
            json_subroot = dict()
            for key, value in self.attributes[branch_name].items():
                json_subroot[key] = self.trans_json_attr(value)
            json_root[branch_name] = json_subroot
        return json_dumps(json_root)

    def __str__(self):
        return self.to_json()

    def from_string(self, json_string: str):
        tmp_dict = json_loads(json_string)

        for branch_name, branch_value in tmp_dict.items():
            self.build_branch(branch_name, **branch_value)
