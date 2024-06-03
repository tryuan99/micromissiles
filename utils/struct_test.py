from absl.testing import absltest

from utils.struct import Struct, StructFields, StructFieldType, Union


class TestUnion(Union):
    """Test union."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "uint32": (StructFieldType.UINT32, 1),
            "uint8": (StructFieldType.UINT8, 1),
        }


class TestNestedStruct(Struct):
    """Test nested struct."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "uint32": (StructFieldType.UINT32, 1),
            "union": (StructFieldType.UNION, 1, TestUnion),
            "uint8": (StructFieldType.UINT8, 1),
        }


class TestStruct(Struct):
    """Test struct."""

    @classmethod
    def fields(cls) -> StructFields:
        """Returns a dictionary mapping each field name to its size in bytes,
        the array length, and an optional struct.
        """
        return {
            "char": (StructFieldType.CHAR, 1),
            "uint8": (StructFieldType.UINT8, 1),
            "int32_array": (StructFieldType.INT32, 4),
            "struct": (StructFieldType.STRUCT, 1, TestNestedStruct),
            "union": (StructFieldType.UNION, 1, TestUnion),
        }


class StructTestCase(absltest.TestCase):

    def setUp(self):
        self.test_struct = TestStruct(
            bytearray(
                b"\x01\xAC\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B"
                b"\x0C\x0D\x0E\x0F\xAA\xBB\xCC\xDD\x12\x34\x56\x78\xFF"
                b"\x31\x41\x59\x26"))

    def test_get_single_element(self):
        self.assertEqual(self.test_struct.get("char"), b"\x01")
        self.assertEqual(self.test_struct.get("uint8"), 0xAC)

    def test_set_single_element(self):
        self.test_struct.set("char", b"\xFF")
        self.test_struct.set("uint8", 200)
        self.assertEqual(self.test_struct.get("char"), b"\xFF")
        self.assertEqual(self.test_struct.get("uint8"), 200)

    def test_get_array(self):
        self.assertEqual(self.test_struct.get("int32_array", index=0),
                         0x03020100)
        self.assertEqual(self.test_struct.get("int32_array"),
                         [0x03020100, 0x07060504, 0x0B0A0908, 0x0F0E0D0C])

    def test_set_array(self):
        self.test_struct.set("int32_array", 1048576, index=2)
        self.assertEqual(self.test_struct.get("int32_array", index=2), 1048576)
        self.test_struct.set("int32_array",
                             [314159265, 27182818, -1000000, 141421])
        self.assertEqual(self.test_struct.get("int32_array"),
                         [314159265, 27182818, -1000000, 141421])

    def test_get_union(self):
        union = self.test_struct.get("union")
        self.assertEqual(union.get("uint32"), 0x26594131)
        self.assertEqual(union.get("uint8"), 0x31)

    def test_set_union(self):
        union = TestUnion(b"\x27\x18\x28\x18")
        self.test_struct.set("union", union)
        self.assertEqual(
            self.test_struct.get("union").get("uint32"), 0x18281827)
        self.assertEqual(self.test_struct.get("union").get("uint8"), 0x27)

    def test_get_struct(self):
        struct = self.test_struct.get("struct")
        self.assertEqual(struct.get("uint32"), 0xDDCCBBAA)
        self.assertEqual(struct.get("uint8"), 0xFF)
        self.assertEqual(struct.get("union").get("uint32"), 0x78563412)
        self.assertEqual(struct.get("union").get("uint8"), 0x12)

    def test_set_struct(self):
        struct = TestStruct(b"\x27\x18\x28\x18\x62\x83\x18\x53\x00")
        self.test_struct.set("struct", struct)
        self.assertEqual(
            self.test_struct.get("struct").get("uint32"), 0x18281827)
        self.assertEqual(self.test_struct.get("struct").get("uint8"), 0x00)
        self.assertEqual(
            self.test_struct.get("struct").get("union").get("uint32"),
            0x53188362)
        self.assertEqual(
            self.test_struct.get("struct").get("union").get("uint8"), 0x62)

    def test_get_buffer(self):
        self.assertEqual(
            self.test_struct.get_buffer(),
            bytearray(
                b"\x01\xAC\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B"
                b"\x0C\x0D\x0E\x0F\xAA\xBB\xCC\xDD\x12\x34\x56\x78\xFF"
                b"\x31\x41\x59\x26"))
        self.assertEqual(self.test_struct.get_buffer(start=12, end=18),
                         bytearray(b"\x0A\x0B\x0C\x0D\x0E\x0F"))
        self.assertEqual(self.test_struct.get_buffer(end=2),
                         bytearray(b"\x01\xAC"))

    def test_set_buffer(self):
        self.test_struct.set_buffer(bytearray(5), start=6)
        self.assertEqual(
            self.test_struct.get_buffer(),
            bytearray(
                b"\x01\xAC\x00\x01\x02\x03\x00\x00\x00\x00\x00\x09\x0A\x0B"
                b"\x0C\x0D\x0E\x0F\xAA\xBB\xCC\xDD\x12\x34\x56\x78\xFF"
                b"\x31\x41\x59\x26"))

    def test_buffer(self):
        struct = TestStruct()
        struct.set("char", b"\x01")
        struct.set("uint8", 0xAC)
        struct.set("int32_array",
                   [0x03020100, 0x07060504, 0x0B0A0908, 0x0F0E0D0C])

        nested_struct = TestNestedStruct()
        nested_struct.set("uint32", 0xDDCCBBAA)
        nested_struct.set("uint8", 0xFF)
        nested_union = TestUnion()
        nested_union.set("uint32", 0x78563412)
        nested_struct.set("union", nested_union)
        struct.set("struct", nested_struct)

        nested_union = TestUnion()
        nested_union.set("uint32", 0x26594131)
        struct.set("union", nested_union)
        self.assertEqual(struct.buffer, self.test_struct.buffer)

    def test_invalid_field(self):
        with self.assertRaises(ValueError):
            self.test_struct.get("error")


if __name__ == "__main__":
    absltest.main()
