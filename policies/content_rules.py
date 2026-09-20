PROHIBITED_CLAIMS = {
    "guaranteed",
    "guaranteed income",
    "no risk",
    "instant wealth",
    "risk free",
}


def check_content_compliance(subject: str, body: str) -> dict:
    normalized_subject = subject.lower()
    normalized_body = body.lower()
    blocked_terms = sorted({term for term in PROHIBITED_CLAIMS if term in normalized_subject or term in normalized_body})
    return {
        "approved": not blocked_terms,
        "blocked_terms": blocked_terms,
        "reason": None if not blocked_terms else "Prohibited claim detected",
    }
