"""
Cryptographic helpers (PROVIDED).
You may use these in your script interpreter and verifier.
Do not modify the function signatures used by the autograder.
"""
import hashlib
from ecdsa import VerifyingKey, BadSignatureError, SECP256k1
from ecdsa.util import sigdecode_string


def ripemd160(data: bytes) -> bytes:
    """RIPEMD160 digest. Uses OpenSSL if available, else pycryptodome."""
    try:
        h = hashlib.new("ripemd160")
    except ValueError:
        from Crypto.Hash import RIPEMD160
        h = RIPEMD160.new()
    h.update(data)
    return h.digest()


def hash160(data: bytes) -> bytes:
    """RIPEMD160(SHA256(data)). Returns 20-byte digest."""
    sha = hashlib.sha256(data).digest()
    return ripemd160(sha)


def hash256(data: bytes) -> bytes:
    """SHA256(SHA256(data)). Returns 32-byte digest."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def verify_signature(pubkey: bytes, message: bytes, signature: bytes) -> bool:
    """
    Verify ECDSA signature. Uses secp256k1 (Bitcoin curve).
    pubkey: raw 33-byte compressed or 65-byte uncompressed public key.
    message: the 32-byte hash that was signed (e.g. hash256 of serialized tx).
    signature: raw 64-byte (r,s). Returns True iff signature is valid.
    """
    try:
        vk = VerifyingKey.from_string(pubkey, curve=SECP256k1)
        return vk.verify_digest(signature, message, sigdecode=sigdecode_string)
    except (BadSignatureError, Exception):
        return False
