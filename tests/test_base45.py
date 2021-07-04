import unittest

from qrlt.base45 import b45decode, b45encode


class Base45Test(unittest.TestCase):
    TEST_VECTORS = (
        # RFC test vectors
        # src: https://datatracker.ietf.org/doc/draft-faltstrom-base45/
        (b'AB', 'BB8'),
        (b'Hello!!', '%69 VD92EX0'),
        (b'base-45', 'UJCLQE7W581'),
        (b'ietf!', 'QED8WEX0'),

        # Correct handling of 0x00-bytes
        (b'\x00', '00'),
        (b'\x00\x00', '000'),

        (b'', ''),
    )

    TEST_VECTORS_BAD = (
        'ZZZ',
        'Z',
        '0000',
    )

    def test_10_decode(self):
        for decoded, encoded in self.TEST_VECTORS:
            with self.subTest(decoded):
                self.assertEqual(b45decode(encoded), decoded)

    def test_11_decode_bad(self):
        for item in self.TEST_VECTORS_BAD:
            with self.subTest(item):
                with self.assertRaises(ValueError):
                    b45decode(item)

    def test_20_encode(self):
        for decoded, encoded in self.TEST_VECTORS:
            with self.subTest(decoded):
                self.assertEqual(b45encode(decoded), encoded)
