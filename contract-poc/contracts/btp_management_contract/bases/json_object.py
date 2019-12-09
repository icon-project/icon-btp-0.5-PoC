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

from iconservice import *


class Attribute:
    def __init__(self, name: str):
        self.name = '_'+name

    def __get__(self, instance, owner):
        return getattr(instance, self.name, str())

    def __set__(self, instance, value):
        setattr(instance, self.name, value)
        instance._init = True


class AddressAttr(Attribute):
    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance, value):
        if not value:
            pass
        elif isinstance(value, str):
            super().__set__(instance, Address.from_string(value))
        elif isinstance(value, Address):
            super().__set__(instance, value)


class IntAttr(Attribute):
    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance, value):
        if isinstance(value, int):
            super().__set__(instance, value)
        elif isinstance(value, str):
            super().__set__(instance, int(value, 16))


class BoolAttr(Attribute):
    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    def __set__(self, instance, value):
        if isinstance(value, bool):
            super().__set__(instance, value)
        elif isinstance(value, str):
            if value == "True":
                super().__set__(instance, True)
            elif value == "False":
                super().__set__(instance, False)
            else:
                # raise value error
                pass


class DictAttr(Attribute):
    def __get__(self, instance, owner):
        return getattr(instance, self.name, "{}")

    def __set__(self, instance, value):
        setattr(instance, self.name, value)


class JsonObject:
    def __init__(self):
        self._attributes = {}

    @property
    def attributes(self):
        return self._attributes

    def set_from_dict(self, dict_obj: dict):
        self._attributes = dict_obj

    def __str__(self):
        tmp_dict = dict()
        for key, value in self._attributes.items():
            tmp_dict[key] = self.trans_json_attr(value)
        return json_dumps(tmp_dict)

    @staticmethod
    def trans_json_attr(value):
        if isinstance(value, Address):
            return str(value)
        if isinstance(value, bool):
            return str(value)
        elif isinstance(value, int) or isinstance(value, bool) or isinstance(value, str):
            return value
        elif isinstance(value, dict):
            return json_dumps(value)

    @classmethod
    def json_build(cls, **kwargs):
        obj = cls()
        for name, value in kwargs.items():
            setattr(obj,name,value)
            obj._attributes[name] = value
        return obj

    @classmethod
    def from_string(cls, dumped_obj):
        obj = cls()
        obj.set_from_dict(json_loads(dumped_obj))
        return obj






