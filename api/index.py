# -*- coding: utf-8 -*-
"""
Flask web app για το Quiz - Vercel compatible.
Τοπικά: python api/index.py
Vercel: deploy μέσω `vercel` CLI ή GitHub integration.
"""
import json
import os
import random
import uuid
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-prod")

HERE = os.path.dirname(os.path.abspath(__file__))
# Try same folder first (Vercel), fall back to project root (local)
QUESTIONS_FILE = os.path.join(HERE, "questions.json")
if not os.path.exists(QUESTIONS_FILE):
    QUESTIONS_FILE = os.path.join(os.path.dirname(HERE), "questions.json")

with open(QUESTIONS_FILE, encoding="utf-8") as f:
    QUESTIONS = json.load(f)

OPTIONS = {"A": "ΝΑΙ", "B": "ΟΧΙ"}

# In-memory test sessions. For Vercel (stateless), state is kept in the cookie via Flask session.
# For larger deployments use a DB / Redis.

INDEX_HTML = """
<!doctype html>
<html lang="el">
<head>
<meta charset="utf-8">
<title>Quiz - GREEN AI & Βιώσιμη Καινοτομία</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { font-family: system-ui, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; background:#f7faf7; color:#1b2a1b; }
  h1 { color:#2e7d32; }
  .card { background:#fff; border-radius:12px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,.06); margin-bottom:20px; }
  button, .btn { background:#2e7d32; color:#fff; border:none; padding:12px 20px; border-radius:8px; font-size:16px; cursor:pointer; text-decoration:none; display:inline-block; margin:4px; }
  button:hover { background:#1b5e20; }
  .opt { display:block; margin:10px 0; padding:12px; border:2px solid #ddd; border-radius:8px; cursor:pointer; }
  .opt:hover { border-color:#2e7d32; background:#f1f8f1; }
  .opt input { margin-right:10px; }
  .progress { color:#666; font-size:14px; margin-bottom:10px; }
  .correct { color:#2e7d32; font-weight:bold; }
  .wrong { color:#c62828; font-weight:bold; }
  .qtext { font-size:18px; margin: 12px 0 20px; }
  .num { color:#888; font-size:13px; }
  .result-q { padding:10px; border-left:4px solid #ddd; margin:10px 0; background:#fafafa; }
  .result-q.ok { border-color:#2e7d32; }
  .result-q.bad { border-color:#c62828; }
</style>
</head>
<body>
<div class="card">
  <h1>Τράπεζα Θεμάτων</h1>
  <p>GREEN AI & Βιώσιμη Καινοτομία — {{ total }} ερωτήσεις διαθέσιμες</p>
  <p>Επίλεξε μέγεθος τεστ:</p>
  <a class="btn" href="{{ url_for('start', n=10) }}">10 ερωτήσεις</a>
  <a class="btn" href="{{ url_for('start', n=20) }}">20 ερωτήσεις</a>
  <a class="btn" href="{{ url_for('start', n=30) }}">30 ερωτήσεις</a>
  <a class="btn" href="{{ url_for('start', n=total) }}">Όλες ({{ total }})</a>
</div>
</body></html>
"""

QUESTION_HTML = """
<!doctype html>
<html lang="el"><head>
<meta charset="utf-8"><title>Ερώτηση {{ idx+1 }}/{{ total }}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { font-family: system-ui, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; background:#f7faf7; }
  .card { background:#fff; border-radius:12px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,.06); }
  button { background:#2e7d32; color:#fff; border:none; padding:12px 24px; border-radius:8px; font-size:16px; cursor:pointer; }
  button:hover { background:#1b5e20; }
  .opt { display:block; margin:10px 0; padding:12px; border:2px solid #ddd; border-radius:8px; cursor:pointer; }
  .opt:hover { border-color:#2e7d32; background:#f1f8f1; }
  .opt input { margin-right:10px; }
  .progress { color:#666; font-size:14px; margin-bottom:10px; }
  .qtext { font-size:18px; margin: 12px 0 20px; }
  .num { color:#888; font-size:13px; }
</style></head><body>
<div class="card">
  <div class="progress">Ερώτηση {{ idx+1 }} από {{ total }} — Score μέχρι τώρα: {{ score }}</div>
  <div class="num">Αρχικό #{{ q.num }}</div>
  <div class="qtext">{{ q.question }}</div>
  <form method="post" action="{{ url_for('answer') }}">
    <label class="opt"><input type="radio" name="ans" value="A" required>A. ΝΑΙ</label>
    <label class="opt"><input type="radio" name="ans" value="B">B. ΟΧΙ</label>
    <button type="submit">Επόμενη →</button>
  </form>
</div></body></html>
"""

RESULT_HTML = """
<!doctype html>
<html lang="el"><head>
<meta charset="utf-8"><title>Αποτέλεσμα</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { font-family: system-ui, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; background:#f7faf7; }
  .card { background:#fff; border-radius:12px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,.06); margin-bottom:20px; }
  h1 { color:#2e7d32; }
  .score { font-size:48px; color:#2e7d32; font-weight:bold; }
  .result-q { padding:12px; border-left:4px solid #ddd; margin:10px 0; background:#fafafa; border-radius:4px; }
  .result-q.ok { border-color:#2e7d32; }
  .result-q.bad { border-color:#c62828; }
  .btn { background:#2e7d32; color:#fff; padding:12px 20px; border-radius:8px; text-decoration:none; display:inline-block; margin-top:10px; }
  .lbl-ok { color:#2e7d32; font-weight:bold; }
  .lbl-bad { color:#c62828; font-weight:bold; }
</style></head><body>
<div class="card">
  <h1>Αποτέλεσμα</h1>
  <div class="score">{{ score }}/{{ total }}</div>
  <div>{{ pct }}%</div>
  <a class="btn" href="{{ url_for('home') }}">Νέο τεστ</a>
</div>
<div class="card">
  <h2>Λεπτομέρειες</h2>
  {% for r in results %}
    <div class="result-q {{ 'ok' if r.correct else 'bad' }}">
      <div><strong>#{{ r.num }}.</strong> {{ r.question }}</div>
      <div>Η απάντησή σου: <span class="{{ 'lbl-ok' if r.correct else 'lbl-bad' }}">{{ r.your }}. {{ r.your_text }}</span></div>
      {% if not r.correct %}<div>Σωστή: <span class="lbl-ok">{{ r.right }}. {{ r.right_text }}</span></div>{% endif %}
    </div>
  {% endfor %}
</div>
</body></html>
"""


@app.route("/")
def home():
    session.clear()
    return render_template_string(INDEX_HTML, total=len(QUESTIONS))


@app.route("/start/<int:n>")
def start(n):
    n = max(1, min(n, len(QUESTIONS)))
    indices = random.sample(range(len(QUESTIONS)), n)
    session["indices"] = indices
    session["idx"] = 0
    session["answers"] = []
    return redirect(url_for("question"))


@app.route("/q")
def question():
    indices = session.get("indices")
    if not indices:
        return redirect(url_for("home"))
    idx = session.get("idx", 0)
    if idx >= len(indices):
        return redirect(url_for("result"))
    q = QUESTIONS[indices[idx]]
    score = sum(1 for a in session.get("answers", []) if a["correct"])
    return render_template_string(QUESTION_HTML, q=q, idx=idx, total=len(indices), score=score)


@app.route("/answer", methods=["POST"])
def answer():
    indices = session.get("indices")
    if not indices:
        return redirect(url_for("home"))
    idx = session.get("idx", 0)
    ans = request.form.get("ans", "")
    q = QUESTIONS[indices[idx]]
    answers = session.get("answers", [])
    answers.append({
        "num": q["num"],
        "your": ans,
        "correct": ans == q["correct"],
    })
    session["answers"] = answers
    session["idx"] = idx + 1
    if session["idx"] >= len(indices):
        return redirect(url_for("result"))
    return redirect(url_for("question"))


@app.route("/result")
def result():
    indices = session.get("indices")
    answers = session.get("answers", [])
    if not indices or not answers:
        return redirect(url_for("home"))
    results = []
    for a, qi in zip(answers, indices):
        q = QUESTIONS[qi]
        results.append({
            "num": q["num"],
            "question": q["question"],
            "your": a["your"],
            "your_text": OPTIONS.get(a["your"], "?"),
            "right": q["correct"],
            "right_text": OPTIONS[q["correct"]],
            "correct": a["correct"],
        })
    score = sum(1 for r in results if r["correct"])
    total = len(results)
    pct = score * 100 // total if total else 0
    return render_template_string(RESULT_HTML, results=results, score=score, total=total, pct=pct)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
