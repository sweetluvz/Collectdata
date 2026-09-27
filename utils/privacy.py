import re

# The repository is public, so phone numbers in listing titles/descriptions are masked before saving.
# Sellers often obfuscate numbers (drop the leading 0, glue letters or symbols in front), so every run of
# 9-11 digits is masked unless its context clearly marks it as a price.
DIGIT_RUN = re.compile(r"(?<!\d)\+?\d(?:[\s.\-]?\d){8,10}(?!\d)")
PRICE_AFTER = re.compile(r"\s*(?:vn[dđ]|đồng|dong|triệu|tỷ|ty|tr|usd|đ)(?!\w)|\s*[₫$]", re.IGNORECASE)
PRICE_BEFORE = re.compile(r"(?:giá|gia|price)[^\d\n]{0,20}$", re.IGNORECASE)


def mask_phones(text):
    text = text or ""

    def replace(m):
        if PRICE_AFTER.match(text, m.end()) or PRICE_BEFORE.search(text[max(0, m.start() - 30):m.start()]):
            return m.group()
        return "[SĐT]"

    return DIGIT_RUN.sub(replace, text)
