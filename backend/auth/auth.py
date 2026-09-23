import hashlib
import hmac
import os

ITERATIONS = 100_000


def _derive_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)


def hash_password(password, salt=None):
    """Επιστρέφει 'salt:hash' σε hex. Το salt είναι τυχαίο, ώστε ίδιοι κωδικοί να δίνουν διαφορετικό hash."""
    if salt is None:
        salt = os.urandom(16)
    return salt.hex() + ":" + _derive_hash(password, salt).hex()


def verify_password(password, stored_hash):
    salt_hex, hash_hex = stored_hash.split(":")
    new_hash = _derive_hash(password, bytes.fromhex(salt_hex)).hex()
    return hmac.compare_digest(new_hash, hash_hex)
