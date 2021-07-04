from datetime import datetime
import unittest

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from freezegun import freeze_time
import importlib_resources

from qrlt.certificate import InvalidCertificateError, NationalCertificate


class NationalCertificateTest(unittest.TestCase):
    TEST_PUBLIC_KEY: rsa.RSAPublicKey = serialization.load_pem_public_key(
        importlib_resources.files('tests').joinpath('public.pem').read_bytes()
    )

    TEST_CERTIFICATE = importlib_resources.files('tests').joinpath('certificate.txt').read_text()

    TEST_CERTIFICATE_DATA = {
        'first_name': 'FIRST',
        'last_name': 'LAST',
        'birth_year': 1900,
        'issued': datetime(year=2021, month=6, day=29, hour=9, minute=40, second=46, microsecond=509000),
        'valid_until': datetime(year=2021, month=7, day=6, hour=9, minute=40, second=46, microsecond=509000),
        't': 'g',
    }

    @classmethod
    def setUpClass(cls):
        NationalCertificate.PUBLIC_KEY = cls.TEST_PUBLIC_KEY

    @freeze_time('2021-07-04')
    def test_01_good(self):
        certificate = NationalCertificate(self.TEST_CERTIFICATE)

        for attribute, value in self.TEST_CERTIFICATE_DATA.items():
            self.assertEqual(getattr(certificate, attribute), value)

    @freeze_time('2021-06-01')
    def test_02_issued_in_future(self):
        with self.assertRaises(InvalidCertificateError) as e:
            NationalCertificate(self.TEST_CERTIFICATE)

        self.assertEqual(e.exception.message, 'Issued in the future')

    @freeze_time('2021-08-01')
    def test_03_expired(self):
        with self.assertRaises(InvalidCertificateError) as e:
            NationalCertificate(self.TEST_CERTIFICATE)

        self.assertEqual(e.exception.message, 'Expired')

    @freeze_time('2021-07-04')
    def test_04_invalid_signature(self):
        test_certificate_invalid = self.TEST_CERTIFICATE[:-1]

        with self.assertRaises(InvalidCertificateError) as e:
            NationalCertificate(test_certificate_invalid)

        self.assertEqual(e.exception.message, 'Invalid signature')