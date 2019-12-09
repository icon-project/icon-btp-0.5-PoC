# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
class Hash32(bytes):
    size = 32
    prefix = "0x"

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        if cls.size is not None and cls.size != len(self):
            raise RuntimeError

        return self

    def __repr__(self):
        type_name = type(self).__qualname__
        return type_name + "(" + super().__repr__() + ")"

    def __str__(self):
        type_name = type(self).__qualname__
        return type_name + "(" + self.hex_xx() + ")"

    @classmethod
    def new(cls):
        """
        create sized value.
        :return:
        """
        return cls(bytes(cls.size) if cls.size else 0)

    @classmethod
    def empty(cls):
        return cls.new()

    def hex_xx(self):
        if self.prefix:
            return self.prefix + self.hex()
        return self.hex()

    def hex_0x(self):
        return self.prefix + self.hex()