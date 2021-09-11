import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = "dev-p498f049.us.auth0.com"
ALGORITHMS = ["RS256"]
API_AUDIENCE = "drinks"

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

def get_token_auth_header():
    """
    Validates a token authorization header and returns the token
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthError("Missing headers", 401)
    header_parts = auth_header.split(" ")
    if header_parts[0] != "header" or len(header_parts) != 2:
        raise AuthError("Malformed headers or missing token", 401)
    return header_parts[1]


def check_permissions(permission, payload):
    """
    Checks if permissions are included in the payload, otherwises raises an
    AuthError
    :param permission: string permission (i.e. 'post:drink')
    :param payload: decoded jwt payload
    """
    if "permissions" not in payload:
        raise AuthError("Missing permissions", 401)
    permissions = payload.get("permissions")
    if not permissions or permission not in permissions:
        raise AuthError("Insufficient permissions", 403)
    return True


def verify_decode_jwt(token):
    """
    Validates a JWT to ensure it:
    - is an Auth0 token with key id (kid)
    - is verified using Auth0 /.well-known/jwks.json
    - uses valid claims
    :return: decoded payload
    """
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    keyset = json.loads(urlopen(url).read())["keys"]
    unverified_header = jwt.get_unverified_header(token)
    rsa = None
    if "kid" not in unverified_header.keys():
        raise AuthError("Invalid header", 401)
    for key in keyset:
        if key["kid"] == unverified_header["kid"]:
            rsa = {
                "e": key["e"],
                "kid": key["kid"],
                "kty": key["kty"],
                "n": key["n"],
                "use": key["use"],
            }
    try:
        if rsa:
            return jwt.decode(
                token,
                json.dumps(rsa),
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
    except Exception as e:
        raise AuthError(e, 401)


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
