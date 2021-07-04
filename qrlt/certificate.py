from datetime import datetime
import json

import importlib_resources
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from .base45 import b45decode


class InvalidCertificateError(Exception):
    def __init__(self, message):
        self.message = message


class NationalCertificate:
    PUBLIC_KEY: rsa.RSAPublicKey = serialization.load_pem_public_key(
        importlib_resources.files('qrlt').joinpath('public.pem').read_bytes()
    )

    __slots__ = (
        'first_name',
        'last_name',
        'birth_year',
        'issued',
        'valid_until',
        't',

        '_base45'
    )

    def __init__(self, data_b45: str):
        self._base45 = data_b45

        data_length, data_b45 = data_b45.split('$', 1)
        data_length = int(data_length)

        payload_b45 = data_b45[:data_length]
        signature = b45decode(data_b45[data_length:])

        try:
            self.verify(payload_b45.encode(), signature)
        except InvalidSignature as e:
            raise InvalidCertificateError('Invalid signature') from e

        payload = json.loads(b45decode(payload_b45))

        self.first_name = payload['fn']
        self.last_name = payload['ln']
        self.birth_year = payload['by']
        self.issued = datetime.utcfromtimestamp(payload['iss'] / 1000)
        self.valid_until = datetime.utcfromtimestamp(payload['vt'] / 1000)
        self.t = payload['t']

        now = datetime.utcnow()

        if self.issued > now:
            raise InvalidCertificateError('Issued in the future')

        if self.valid_until < now:
            raise InvalidCertificateError('Expired')

    def __str__(self):
        return (
            f'{self.first_name} {self.last_name} ({self.birth_year})\n'
            f'Issued: {self.issued}\n'
            f'Valid until: {self.valid_until}'
        )

    def __repr__(self):
        return f'{self.__class__.__name__}({self._base45:!r})'

    @classmethod
    def verify(cls, data: bytes, signature: bytes):
        cls.PUBLIC_KEY.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
