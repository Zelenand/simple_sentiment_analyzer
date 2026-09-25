from functools import lru_cache

import nltk
from nltk.corpus import stopwords
from ruwordnet import RuWordNet
import csv

# ---------------------------------------------------------
# NLTK: стоп-слова
# ---------------------------------------------------------

try:
    STOP_WORDS = set(stopwords.words("russian"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    STOP_WORDS = set(stopwords.words("russian"))



LEXICON = {}

with open("data/kartaslovsent.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")

    for row in reader:
        LEXICON[row["term"]] = float(row["value"])


_ruwordnet = RuWordNet()

@lru_cache(maxsize=100_000)
def get_synonym(word: str) -> str:
    """
    Возвращает первую лемму слов из того же synset, что и word.
    """

    synonym = word
    try:
        senses =_ruwordnet.get_senses(word)
        if len(senses) > 0:
            synonym = senses[0].synset.senses[0].lower().replace("_", " ")
        
    except Exception:
        pass

    return synonym


INTENSIFIERS = {
    "очень": 1.5,
    "крайне": 1.8,
    "чрезвычайно": 2.0,
    "абсолютно": 1.8,
    "совершенно": 1.7,
    "максимально": 1.7,
    "реально": 1.3,
    "действительно": 1.3,
    "настолько": 1.4,
    "сильно": 1.5,
}

DIMINISHERS = {
    "немного": 0.5,
    "слегка": 0.5,
    "чуть": 0.5,
    "довольно": 0.8,
    "несколько": 0.7,
    "отчасти": 0.6,
    "почти": 0.7,
}

NEGATIONS = {
    "не",
    "ни",
    "никто",
    "ничто",
    "никогда",
    "нигде",
    "никак",
    "нисколько",
    "нет",
}


if __name__ == "__main__":
    word = "отличный"
    synonym = get_synonym(word)
    print(f"Синоним слова '{word}': {synonym}")

    print(LEXICON)