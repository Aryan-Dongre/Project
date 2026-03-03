import secrets
import hashlib
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_password_reset_token():
    """
     Generates:
     -row_token (random secure string)
     -sign_token (sent to user via email)
     -hashed_token (store in db)
    """

    # generate cryptographically secure random token 
    raw_token = secrets.token_urlsafe(32)

    # sign the token using SECRETE KEY
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    signed_token = serializer.dumps(
                    raw_token,
                    salt=current_app.config["SECURITY_PASSWORD_SALT"]
                    )

    # Hash the raw token 
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

    return signed_token, hashed_token

def verify_signed_token(signed_token):
    """
     Verifies signature and returns raw token if valid.
     Return None if token is tampered.
    """
    
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    try:
        raw_token = serializer.loads(
                    signed_token,
                    salt=current_app.config["SECURITY_PASSWORD_SALT"],
                    max_age=600
                    )
        return raw_token
    except Exception :
        return None


def hash_token(raw_token):
        
        """
        Hash helper (used during verification phase)
        """
        return hashlib.sha256(raw_token.encode()).hexdigest()

