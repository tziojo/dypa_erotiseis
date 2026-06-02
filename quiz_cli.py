# -*- coding: utf-8 -*-
"""
Quiz CLI - Τράπεζα Θεμάτων GREEN AI & Βιώσιμη Καινοτομία
Τρέξτε online σε Replit / Google Colab ή τοπικά: python quiz_cli.py
"""
import json
import random
import os
import sys

QUESTIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.json")

OPTIONS = {"A": "ΝΑΙ", "B": "ΟΧΙ"}


def load_questions():
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def choose_size(total):
    print("\n=== ΤΡΑΠΕΖΑ ΘΕΜΑΤΩΝ - GREEN AI & Βιώσιμη Καινοτομία ===")
    print(f"Διαθέσιμες ερωτήσεις: {total}\n")
    print("Επίλεξε μέγεθος τεστ:")
    print("  1) 10 ερωτήσεις")
    print("  2) 20 ερωτήσεις")
    print("  3) 30 ερωτήσεις")
    print("  4) Όλες (50)")
    while True:
        c = input("Επιλογή (1-4): ").strip()
        if c == "1": return 10
        if c == "2": return 20
        if c == "3": return 30
        if c == "4": return total
        print("Μη έγκυρη επιλογή.")


def run_test(questions, n):
    sample = random.sample(questions, min(n, len(questions)))
    score = 0
    wrong = []
    for i, q in enumerate(sample, 1):
        print(f"\n--- Ερώτηση {i}/{len(sample)} (αρχικό #{q['num']}) ---")
        print(q["question"])
        print("  A. ΝΑΙ")
        print("  B. ΟΧΙ")
        while True:
            ans = input("Απάντηση (A/B): ").strip().upper()
            if ans in ("A", "B"):
                break
            print("Πληκτρολόγησε A ή B.")
        if ans == q["correct"]:
            print("✓ Σωστό!")
            score += 1
        else:
            print(f"✗ Λάθος. Σωστή απάντηση: {q['correct']}. {OPTIONS[q['correct']]}")
            wrong.append(q)

    print("\n" + "=" * 50)
    print(f"ΑΠΟΤΕΛΕΣΜΑ: {score}/{len(sample)} ({score*100//len(sample)}%)")
    print("=" * 50)
    if wrong:
        print("\nΛανθασμένες ερωτήσεις:")
        for q in wrong:
            print(f"  #{q['num']}: {q['question'][:70]}... -> {q['correct']}")


def main():
    questions = load_questions()
    while True:
        n = choose_size(len(questions))
        run_test(questions, n)
        again = input("\nΝέο τεστ; (y/n): ").strip().lower()
        if again != "y":
            print("Καλή μελέτη!")
            break


if __name__ == "__main__":
    main()
