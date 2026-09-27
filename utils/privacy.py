import re

# The repository is public: phone numbers posted in listing titles/descriptions are masked before saving.
PHONE_RE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)")


def mask_phones(text):
    return PHONE_RE.sub("[SĐT]", text or "")
