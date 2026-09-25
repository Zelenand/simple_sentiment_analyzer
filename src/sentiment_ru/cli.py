import argparse
import json
from pathlib import Path

from .analyzer import SentimentAnalyzer

def print_result(result):
    print(f"Текст: {result.text}")
    print(f"Положительная: {result.positive:.3f}")
    print(f"Отрицательная: {result.negative:.3f}")
    print(f"Нейтральная: {result.neutral:.3f}")
    print(f"Compound: {result.compound:.3f}")
    print(f"Метка: {result.label}")
    # print(f"Токены: {', '.join(result.tokens)}")
    # print(f"Нормализованные: {', '.join(result.normalized)}")

def main():
    parser = argparse.ArgumentParser(
        description="Простой анализатор тональности русскоязычного текста"
    )
    parser.add_argument("text", nargs="?", help="Текст для анализа")
    parser.add_argument("--file", type=Path, help="UTF-8 текстовый файл")
    parser.add_argument("--csv", type=Path, help="CSV-файл")
    parser.add_argument("--column", default="text", help="Столбец CSV, по умолчанию text")
    parser.add_argument("--interactive", action="store_true", help="Интерактивный режим")
    parser.add_argument("--json", action="store_true", help="Вывод JSON")
    args = parser.parse_args()

    analyzer = SentimentAnalyzer()

    if args.interactive:
        while True:
            text = input("Введите текст (exit для выхода): ").strip()
            if text.lower() == "exit":
                break
            print(analyzer.analyze(text).label)
        return

    if args.file:
        text = args.file.read_text(encoding="utf-8")
        result = analyzer.analyze(text)
    elif args.csv:
        import csv
        rows = []
        with args.csv.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                result = analyzer.analyze(row[args.column])
                rows.append({
                    "text": row[args.column],
                    "label": result.label,
                    "compound": result.compound
                })
        for row in rows:
            print(f'{row["label"]:8} {row["compound"]:7.3f}  {row["text"]}')
        return
    elif args.text:
        result = analyzer.analyze(args.text)
    else:
        parser.error("Укажите текст, --file, --csv или --interactive")

    print_result(result)
