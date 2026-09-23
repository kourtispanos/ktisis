import secrets

from fastapi import Header, HTTPException

_sessions = {}


def create_session(username):
    token = secrets.token_urlsafe(32)
    _sessions[token] = username
    return token


def end_session(token):
    _sessions.pop(token, None)


def end_user_sessions(username):
    """Κλείνει όλες τις ανοιχτές συνδέσεις ενός χρήστη (π.χ. μετά τη διαγραφή του λογαριασμού)."""
    for token in [t for t, user in _sessions.items() if user == username]:
        del _sessions[token]


def get_token(authorization: str = Header(default="")):
    return authorization.removeprefix("Bearer ").strip()


def require_auth(authorization: str = Header(default="")):
    token = get_token(authorization)
    if token not in _sessions:
        raise HTTPException(status_code=401, detail="Δεν είσαι συνδεδεμένος")
    return _sessions[token]
