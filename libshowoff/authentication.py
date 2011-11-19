import os, bcrypt

def encrypt_password(seed, password):
    """Encrypt given password using seed as an extra salt"""
    return bcrypt.hashpw('%s%s' % (seed, password), bcrypt.gensalt())

def validate_password(seed, password, hash):
    """Validation function for blowfish encrypted password"""
    return bcrypt.hashpw('%s%s' % (seed, password), hash) == hash

