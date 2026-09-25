from dataclasses import dataclass, asdict
import math
import re

from .tokenizer import tokenize
from .normalizer import normalize_tokens
from .lexicon import (
    LEXICON, INTENSIFIERS, DIMINISHERS, NEGATIONS
)

@dataclass
class SentimentResult:
    text: str
    positive: float
    negative: float
    neutral: float
    compound: float
    label: str
    tokens: list[str]
    normalized: list[str]

    def to_dict(self):
        return asdict(self)

class SentimentAnalyzer:
    def __init__(self, negation_window: int = 3):
        self.negation_window = negation_window

    @staticmethod
    def _punctuation_boost(text: str) -> float:
        exclamations = len(re.findall(r"!", text))
        if exclamations == 0:
            return 0.0
        return min(0.8, 0.15 * exclamations)

    @staticmethod
    def _caps_boost(word: str) -> float:
        letters = [c for c in word if c.isalpha()]
        if len(letters) >= 2 and word.upper() == word and word.lower() != word:
            return 1.25
        return 1.0

    @staticmethod
    def _normalize_compound(score: float) -> float:
        return max(-1.0, min(1.0, score / math.sqrt(score * score + 12.0)))

    def analyze(self, text: str) -> SentimentResult:
        raw_tokens = tokenize(text)
        norm_tokens = normalize_tokens(raw_tokens)

        score = 0.0
        positive_raw = 0.0
        negative_raw = 0.0

        previous_modifiers = []
        negation_left = 0

        for i, token in enumerate(norm_tokens):

            if token.kind != "word":
                if token.kind == "exclamation":
                    score += math.copysign(self._punctuation_boost(text), score) if score else 0
                continue

            lemma = token.lemma

            if lemma in NEGATIONS:
                negation_left = self.negation_window
                continue

            if lemma in INTENSIFIERS:
                previous_modifiers.append(INTENSIFIERS[lemma])
                continue

            if lemma in DIMINISHERS:
                previous_modifiers.append(DIMINISHERS[lemma])
                continue

            if lemma not in LEXICON:
                if negation_left:
                    negation_left -= 1
                continue

            value = LEXICON[lemma]

            for modifier in previous_modifiers:
                value *= modifier
            previous_modifiers.clear()

            value *= self._caps_boost(token.original)

            if negation_left:
                # Для словесного отрицания меняем знак и немного ослабляем эффект
                value *= -0.90
                negation_left = 0

            score += value
            positive_raw += max(value, 0)
            negative_raw += min(value, 0)

        # Эмоциональная пунктуация усиливает уже найденную полярность.
        punct = self._punctuation_boost(text)
        if punct and score:
            score *= (1.0 + punct)

        compound = self._normalize_compound(score)

        if compound >= 0.05:
            label = "позитивный"
        elif compound <= -0.05:
            label = "негативный"
        else:
            label = "нейтральный"

        total = abs(positive_raw) + abs(negative_raw)
        if total == 0:
            positive = negative = 0.0
            neutral = 1.0
        else:
            positive = abs(positive_raw) / total
            negative = abs(negative_raw) / total
            neutral = max(0.0, 1.0 - positive - negative)

        return SentimentResult(
            text=text,
            positive=round(positive, 4),
            negative=round(negative, 4),
            neutral=round(neutral, 4),
            compound=round(compound, 4),
            label=label,
            tokens=[t.text for t in raw_tokens],
            normalized=[t.lemma for t in norm_tokens if t.kind == "word" and not t.is_stopword],
        )
