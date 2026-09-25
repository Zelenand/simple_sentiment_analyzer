import re
from dataclasses import dataclass

TOKEN_RE = re.compile(
    r"[A-Za-zА-Яа-яЁё0-9]+(?:[-'][A-Za-zА-Яа-яЁё0-9]+)*|"
    r"[!?]+|[.,:;…]+|"
    r"[\U0001F300-\U0001FAFF]|"
    r"[:;=8xX][\-^']?[)(DPp]"
)

@dataclass(frozen=True)
class Token:
    text: str
    kind: str

def tokenize(text: str) -> list[Token]:
    tokens = []
    for match in TOKEN_RE.finditer(text):
        value = match.group(0)
        if re.fullmatch(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-'][A-Za-zА-Яа-яЁё0-9]+)*", value):
            kind = "word"
        elif re.fullmatch(r"[!?]+", value):
            kind = "exclamation"
        elif re.fullmatch(r"[.,:;…]+", value):
            kind = "punctuation"
        else:
            kind = "other"
        tokens.append(Token(value, kind))
    return tokens
