# *****************************************************************************
#   Copyright 2019 Karl Einar Nelson
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# *****************************************************************************
import jpype
from jpype import java
from jpype.pickle import JPickler, JUnpickler
import common

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class PickleTestCase(common.JPypeTestCase):
    def setUp(self):
        common.JPypeTestCase.setUp(self)

    def testString(self):
        s = java.lang.String("test")
        with open("test.pic","wb") as fd:
            JPickler(fd).dump(s)
        with open("test.pic","rb") as fd:
            s2 = JUnpickler(fd).load()
        self.assertEqual(s,s2)

    def testList(self):
        s = java.util.ArrayList()
        s.add("test")
        s.add("this")
        with open("test.pic","wb") as fd:
            JPickler(fd).dump(s)
        with open("test.pic","rb") as fd:
            s2 = JUnpickler(fd).load()
        self.assertEqual(s2.get(0), "test")
        self.assertEqual(s2.get(1), "this")

    def testMixed(self):
        d = {}
        d["array"] = java.util.ArrayList()
        d["string"] = java.lang.String("food")
        with open("test.pic","wb") as fd:
            JPickler(fd).dump(d)
        with open("test.pic","rb") as fd:
            d2 = JUnpickler(fd).load()
        self.assertEqual(d2['string'], "food")
        self.assertIsInstance(d2['array'], java.util.ArrayList)

    def testFail(self):
        s = java.lang.Object()
        with self.assertRaises(java.io.NotSerializableException):
            with open("test.pic","wb") as fd:
                JPickler(fd).dump(s)
     

