# *****************************************************************************
#   Copyright 2004-2008 Steve Menard
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# *****************************************************************************
import sys
import jpype
from jpype import JPackage, JArray, JByte, java, JClass
import common

if sys.version > '3':
    unicode = str


def haveNumpy():
    try:
        import numpy
        return True
    except ImportError:
        return False


class ArrayTestCase(common.JPypeTestCase):

    def setUp(self):
        common.JPypeTestCase.setUp(self)
        self.VALUES = [12234, 1234, 234, 1324, 424, 234, 234, 142, 5, 251, 242, 35, 235, 62,
                       1235, 46, 245132, 51, 2, 3, 4]

    def testReadArray(self):
        t = JClass("jpype.array.TestArray")()
        self.assertNotIsInstance(t, JPackage)

        self.assertCountEqual(self.VALUES, t.i)

        self.assertEqual(t.i[0], self.VALUES[0])
        self.assertCountEqual(self.VALUES[1:-2], t.i[1:-2])

    def testEmptyObjectArray(self):
        ''' Test for strange crash reported in bug #1089302'''
        Test2 = jpype.JPackage('jpype.array').Test2
        test = Test2()
        test.test(test.getValue())

    def testWriteArray(self):
        t = JClass("jpype.array.TestArray")()
        self.assertNotIsInstance(t, JPackage)

        t.i[0] = 32
        self.assertEqual(t.i[0], 32)

        t.i[1:3] = (33, 34)
        self.assertEqual(t.i[1], 33)
        self.assertEqual(t.i[2], 34)

        self.assertCountEqual(t.i[:5], (32, 33, 34, 1324, 424))

    def testObjectArraySimple(self):
        a = JArray(java.lang.String, 1)(2)
        a[1] = "Foo"
        self.assertEqual("Foo", a[1])

    def testByteArraySimple(self):
        a = JArray(JByte)(2)
        a[1] = 2
        self.assertEqual(a[1], 2)

    def testIterateArray(self):
        t = JClass("jpype.array.TestArray")()
        self.assertFalse(isinstance(t, JPackage))

        for i in t.i:
            self.assertNotEqual(i, 0)

    def testGetSubclass(self):
        t = JClass("jpype.array.TestArray")()
        v = t.getSubClassArray()
        self.assertTrue(isinstance(v[0], jpype.java.lang.Integer))

    def testGetArrayAsObject(self):
        t = JClass("jpype.array.TestArray")()
        v = t.getArrayAsObject()

    def testCharArrayAsString(self):
        t = JClass("jpype.array.TestArray")()
        v = t.getCharArray()
        self.assertEqual(str(v), 'avcd')
        self.assertEqual(unicode(v), u'avcd')

    def testByteArrayAsString(self):
        t = JClass("jpype.array.TestArray")()
        v = t.getByteArray()
        self.assertEqual(str(v), 'avcd')

    def testByteArrayIntoVector(self):
        ba = jpype.JArray(jpype.JByte)(b'123')
        v = jpype.java.util.Vector(1)
        v.add(ba)
        self.assertEqual(len(v), 1)
        self.assertNotEqual(v[0], None)

    def testJArrayConversionBool(self):
        expected = [True, False, False, True]
        jarr = jpype.JArray(jpype.JBoolean)(expected)

        self.assertCountEqual(expected, jarr[:])

    def testJArrayConversionChar(self):
        t = JClass("jpype.array.TestArray")()
        v = t.getCharArray()
        self.assertEqual(v[:], 'avcd')
        # FIXME: this returns unicode on windows
        self.assertEqual(str(v[:]), 'avcd')
        self.assertEqual(unicode(v[:]), u'avcd')

    def testJArrayConversionByte(self):
        expected = (0, 1, 2, 3)
        ByteBuffer = jpype.java.nio.ByteBuffer
        bb = ByteBuffer.allocate(4)
        buf = bb.array()
        for i in range(len(expected)):
            buf[i] = expected[i]

        self.assertCountEqual(expected[:], buf[:])

    def testJArrayConversionShort(self):
        # filter out values, which can not be converted to jshort
        self.VALUES = [v for v in self.VALUES if v < (2**16 / 2 - 1)
                       and v > (2**16 / 2 * -1)]
        jarr = jpype.JArray(jpype.JShort)(self.VALUES)
        result = jarr[0: len(jarr)]
        self.assertCountEqual(self.VALUES, result)

        result = jarr[2:10]
        self.assertCountEqual(self.VALUES[2:10], result)

        # TODO: investigate why overflow is being casted on linux, but not on windows
        # with self.assertRaises(jpype._):
        #    jpype.JArray(jpype.JShort)([2**16/2])

    def testJArrayConversionFail(self):
        jarr = jpype.JArray(jpype.JInt)(self.VALUES)
        with self.assertRaises(TypeError):
            jarr[1] = 'a'

    def testJArraySliceLength(self):
        jarr = jpype.JArray(jpype.JInt)(self.VALUES)
        jarr[1:2] = [1]
        with self.assertRaises(ValueError):
            jarr[1:2] = [1,2,3]

    def testJArrayConversionInt(self):
        jarr = jpype.JArray(jpype.JInt)(self.VALUES)
        result = jarr[0: len(jarr)]
        self.assertCountEqual(self.VALUES, result)

        result = jarr[2:10]
        self.assertCountEqual(self.VALUES[2:10], result)

    def testJArrayConversionLong(self):
        jarr = jpype.JArray(jpype.JLong)(self.VALUES)
        result = jarr[0: len(jarr)]
        self.assertCountEqual(self.VALUES, result)

        result = jarr[2:10]
        self.assertCountEqual(self.VALUES[2:10], result)

    def testJArrayPythonTypes(self):
        self.assertEqual(jpype.JArray(
            object).class_.getComponentType(), JClass('java.lang.Object'))
        self.assertEqual(jpype.JArray(
            float).class_.getComponentType(), JClass('java.lang.Double').TYPE)
        self.assertEqual(jpype.JArray(
            str).class_.getComponentType(), JClass('java.lang.String'))
        self.assertEqual(jpype.JArray(
            type).class_.getComponentType(), JClass('java.lang.Class'))

    def testJArrayConversionFloat(self):
        VALUES = [float(x) for x in self.VALUES]
        jarr = jpype.JArray(jpype.JFloat)(VALUES)
        result = jarr[0: len(jarr)]
        self.assertCountEqual(jarr, result)

        result = jarr[2:10]
        self.assertCountEqual(VALUES[2:10], result)

    def testJArrayConversionDouble(self):
        VALUES = [float(x) for x in self.VALUES]
        jarr = jpype.JArray(jpype.JDouble)(VALUES)
        self.assertCountEqual(VALUES, jarr)
        result = jarr[:]
        self.assertCountEqual(VALUES, result)

        result = jarr[2:10]

        self.assertEqual(len(VALUES[2:10]), len(result))
        self.assertCountEqual(VALUES[2:10], result)

        # empty slice
        result = jarr[-1:3]
        expected = VALUES[-1:3]
        self.assertCountEqual(expected, result)

        result = jarr[3:-2]
        expected = VALUES[3:-2]
        self.assertCountEqual(expected, result)

    def testConversionError(self):
        jarr = jpype.JArray(jpype.JInt, 1)(10)
        with self.assertRaises(TypeError):
            jarr[1:2] = [dict()]

        # -1 is returned by python, if conversion fails also, ensure this works
        jarr[1:2] = [-1]

    def testObjectArrayInitial(self):
        l1 = java.util.ArrayList()
        l1.add(0)
        l2 = java.util.ArrayList()
        l2.add(42)
        l3 = java.util.ArrayList()
        l3.add(13)
        jarr = jpype.JArray(java.util.ArrayList, 1)([l1, l2, l3])

        self.assertEqual(l1, jarr[0])
        self.assertEqual(l2, jarr[1])
        self.assertEqual(l3, jarr[2])

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPBoolArray(self):
        import numpy as np
        n = 100
        a = np.random.randint(0, 1, size=n).astype(np.bool)
        jarr = jpype.JArray(jpype.JBoolean)(n)
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPByteArray(self):
        import numpy as np
        n = 100
        a = np.random.randint(-128, 127, size=n).astype(np.byte)
        jarr = jpype.JArray(jpype.JByte)(n)
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPShortArray(self):
        import numpy as np
        n = 100
        a = np.random.randint(-32768, 32767, size=n).astype(np.short)
        jarr = jpype.JArray(jpype.JShort)(n)
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPIntArray(self):
        import numpy as np
        n = 100
        a = np.random.randint(-2**31, 2**31 - 1, size=n).astype(np.int32)
        jarr = jpype.JArray(jpype.JInt)(n)
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPLongArray(self):
        import numpy as np
        n = 100
        # actuall the lower bound should be -2**63 -1, but raises Overflow
        # error in numpy
        a = np.random.randint(-2**63, 2**63 - 1, size=n, dtype=np.int64)
        jarr = jpype.JArray(jpype.JLong)(n)
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPFloatArray(self):
        import numpy as np
        n = 100
        a = np.random.random(n).astype(np.float32)
        jarr = jpype.JArray(jpype.JFloat)(n)
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPDoubleArray(self):
        import numpy as np
        n = 100
        a = np.random.random(n).astype(np.float64)
        jarr = jpype.JArray(jpype.JDouble)(n)
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testInitFromNPIntArray(self):
        import numpy as np
        n = 100
        a = np.random.random(n).astype(np.int)
        jarr = jpype.JArray(jpype.JInt)(a)
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testInitFromNPDoubleArray(self):
        import numpy as np
        n = 100
        a = np.random.random(n).astype(np.float)
        jarr = jpype.JArray(jpype.JDouble)(a)
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testInitFromNPDoubleArrayFloat32(self):
        import numpy as np
        n = 100
        a = np.random.random(n).astype(np.float32)
        jarr = jpype.JArray(jpype.JDouble)(a)
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testInitFromNPDoubleArrayFloat64(self):
        import numpy as np
        n = 100
        a = np.random.random(n).astype(np.float64)
        jarr = jpype.JArray(jpype.JDouble)(a)
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testInitFromNPFloatArrayInt(self):
        import numpy as np
        a = np.array([1, 2, 3], dtype=np.int32)
        jarr = jpype.JArray(jpype.JFloat)(a)
        self.assertCountEqual(a, jarr)

    @common.unittest.skipUnless(haveNumpy(), "numpy not available")
    def testSetFromNPFloatArrayInt(self):
        import numpy as np
        a = np.array([1, 2, 3], np.int32)
        jarr = jpype.JArray(jpype.JFloat)(len(a))
        jarr[:] = a
        self.assertCountEqual(a, jarr)

    def testArrayCtor1(self):
        jobject = jpype.JClass('java.lang.Object')
        jarray = jpype.JArray(jobject)
        self.assertTrue(issubclass(jarray, jpype.JArray))
        self.assertTrue(isinstance(jarray(10), jpype.JArray))

    def testArrayCtor2(self):
        jobject = jpype.JClass('java.util.List')
        jarray = jpype.JArray(jobject)
        self.assertTrue(issubclass(jarray, jpype.JArray))
        self.assertTrue(isinstance(jarray(10), jpype.JArray))

    def testArrayCtor3(self):
        jarray = jpype.JArray("java.lang.Object")
        self.assertTrue(issubclass(jarray, jpype.JArray))
        self.assertTrue(isinstance(jarray(10), jpype.JArray))

    def testArrayCtor4(self):
        jarray = jpype.JArray(jpype.JObject)
        self.assertTrue(issubclass(jarray, jpype.JArray))
        self.assertTrue(isinstance(jarray(10), jpype.JArray))

    def testArrayCtor5(self):
        jarray0 = jpype.JArray("java.lang.Object")
        jarray = jpype.JArray(jarray0)
        self.assertTrue(issubclass(jarray, jpype.JArray))
        self.assertTrue(isinstance(jarray(10), jpype.JArray))

    def testArrayClone(self):
        array = jpype.JArray(jpype.JInt, 2)([[1,2],[3,4]])
        carray = array.clone()
        # Verify the first dimension is cloned
        self.assertFalse(array.equals(carray))
        # Copy is shallow
        self.assertTrue(array[0].equals(carray[0]))

    def testObjectNullArraySlice(self):
        # Check for bug in 0.7.0
        array = jpype.JArray(jpype.JObject)([None,])
        self.assertEqual(array[:], (None,))
