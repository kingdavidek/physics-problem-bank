"""Controller identity, contact, and IP pseudonymisation (S0)."""
import hashlib
import hmac
import os


def controller_name():
    return (os.environ.get('CONTROLLER_NAME') or 'Problem Bank operator').strip()


def privacy_contact_email():
    return (os.environ.get('PRIVACY_CONTACT_EMAIL') or 'privacy@localhost').strip()


def ico_registration_number():
    return (os.environ.get('ICO_REGISTRATION_NUMBER') or '').strip()


def hashed_ip(secret, ip):
    """Keyed hash of an IP for rate-limit buckets. Never store the raw address."""
    key = secret if isinstance(secret, (bytes, bytearray)) else str(secret or '').encode('utf-8')
    value = (ip or 'unknown').encode('utf-8')
    return hmac.new(key, value, hashlib.sha256).hexdigest()[:16]
