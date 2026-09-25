from dataclasses import dataclass
from .tokenizer import Token
from .lexicon import STOP_WORDS, get_synonym
import pymorphy3

_morph = pymorphy3.MorphAnalyzer()

@dataclass(frozen=True)
class NormalizedToken:
    original: str
    lemma: str
    kind: str
    is_stopword: bool

def normalize_tokens(tokens: list[Token]) -> list[NormalizedToken]:
    result = []
    for token in tokens:
        if token.kind != "word":
            result.append(NormalizedToken(token.text, token.text, token.kind, False))
            continue
        lower = token.text.lower()
        parse = _morph.parse(lower)[0]
        lemma = parse.normal_form
        lemma = get_synonym(lemma)
        result.append(
            NormalizedToken(
                original=token.text,
                lemma=lemma,
                kind=token.kind,
                is_stopword=lemma in STOP_WORDS,
            )
        )
    return result

def vocabulary(tokens: list[NormalizedToken]) -> list[str]:
    return [t.lemma for t in tokens if t.kind == "word" and not t.is_stopword]
