# -*- coding: utf-8 -*-
"""
Quiz Web App - GREEN AI & Βιώσιμη Καινοτομία
Standalone local web app. Zero dependencies (μόνο Python 3).

ΤΡΕΞΙΜΟ:
    python3 app.py

Θα ανοίξει αυτόματα ο browser στο http://localhost:8000
"""
import json
import os
import random
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

PORT = 8000

# Load questions from same folder (questions.json) or fall back to embedded
QUESTIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.json")
if os.path.exists(QUESTIONS_PATH):
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        QUESTIONS = json.load(f)
else:
    QUESTIONS = []  # placeholder - questions.json πρέπει να υπάρχει δίπλα στο app.py

HTML = r"""<!doctype html>
<html lang="el">
<head>
<meta charset="utf-8">
<title>Quiz - GREEN AI & Βιώσιμη Καινοτομία</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    margin: 0; padding: 20px;
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    min-height: 100vh;
    color: #1b2a1b;
  }
  .container { max-width: 720px; margin: 0 auto; }
  .card {
    background: #fff; border-radius: 16px; padding: 32px;
    box-shadow: 0 8px 24px rgba(0,0,0,.08);
    margin-bottom: 16px;
  }
  h1 { color: #2e7d32; margin: 0 0 8px; font-size: 28px; }
  h2 { color: #2e7d32; margin: 0 0 16px; }
  .subtitle { color: #555; margin-bottom: 24px; }
  .size-btn {
    display: block; width: 100%; padding: 16px; margin: 8px 0;
    background: #fff; border: 2px solid #2e7d32; color: #2e7d32;
    border-radius: 10px; font-size: 16px; font-weight: 600;
    cursor: pointer; transition: all .15s;
  }
  .size-btn:hover { background: #2e7d32; color: #fff; transform: translateY(-1px); }
  .progress-bar {
    height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden;
    margin-bottom: 16px;
  }
  .progress-fill {
    height: 100%; background: linear-gradient(90deg, #66bb6a, #2e7d32);
    transition: width .3s;
  }
  .meta { color: #666; font-size: 14px; display: flex; justify-content: space-between; margin-bottom: 16px; }
  .qnum { color: #999; font-size: 13px; }
  .qtext { font-size: 19px; line-height: 1.5; margin: 16px 0 28px; color: #1b2a1b; }
  .opt {
    display: block; padding: 16px 20px; margin: 10px 0;
    background: #fafafa; border: 2px solid #e0e0e0; border-radius: 10px;
    cursor: pointer; font-size: 16px; transition: all .15s;
  }
  .opt:hover { border-color: #2e7d32; background: #f1f8f1; transform: translateX(4px); }
  .opt.correct { border-color: #2e7d32; background: #e8f5e9; }
  .opt.wrong { border-color: #c62828; background: #ffebee; }
  .opt.disabled { cursor: default; pointer-events: none; opacity: .7; }
  .opt.correct.disabled, .opt.wrong.disabled { opacity: 1; }
  .letter { display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center;
            background: #2e7d32; color: #fff; border-radius: 50%; margin-right: 12px; font-weight: 700; font-size: 14px; }
  .next-btn, .restart-btn {
    width: 100%; padding: 14px; margin-top: 16px;
    background: #2e7d32; color: #fff; border: none; border-radius: 10px;
    font-size: 16px; font-weight: 600; cursor: pointer; transition: background .15s;
  }
  .next-btn:hover, .restart-btn:hover { background: #1b5e20; }
  .next-btn:disabled { background: #ccc; cursor: not-allowed; }
  .score-big { font-size: 64px; font-weight: 700; color: #2e7d32; text-align: center; margin: 16px 0; }
  .pct { text-align: center; color: #666; font-size: 18px; margin-bottom: 24px; }
  .result-item {
    padding: 14px; border-left: 4px solid #ddd; margin: 10px 0;
    background: #fafafa; border-radius: 0 8px 8px 0;
  }
  .result-item.ok { border-color: #2e7d32; background: #e8f5e9; }
  .result-item.bad { border-color: #c62828; background: #ffebee; }
  .result-q { font-weight: 500; margin-bottom: 6px; }
  .result-a { font-size: 14px; color: #555; }
  .label-ok { color: #2e7d32; font-weight: 700; }
  .label-bad { color: #c62828; font-weight: 700; }
  .feedback { text-align: center; padding: 14px; margin: 16px 0; border-radius: 10px; font-weight: 600; }
  .feedback.ok { background: #e8f5e9; color: #2e7d32; }
  .feedback.bad { background: #ffebee; color: #c62828; }
</style>
</head>
<body>
<div class="container">
  <div id="app"></div>
</div>

<script>
const OPTIONS = { A: "ΝΑΙ", B: "ΟΧΙ" };
let state = {
  questions: [],
  idx: 0,
  answers: [],   // {q, your, correct}
  total: 0
};

async function init() {
  showHome();
}

async function showHome() {
  const res = await fetch("/api/info");
  const data = await res.json();
  const app = document.getElementById("app");
  app.innerHTML = `
    <div class="card">
      <h1>🌱 Τράπεζα Θεμάτων</h1>
      <div class="subtitle">GREEN AI & Βιώσιμη Καινοτομία — ${data.total} ερωτήσεις</div>
      <p>Επίλεξε μέγεθος τεστ:</p>
      <button class="size-btn" onclick="startQuiz(10)">📝 10 ερωτήσεις</button>
      <button class="size-btn" onclick="startQuiz(20)">📋 20 ερωτήσεις</button>
      <button class="size-btn" onclick="startQuiz(30)">📚 30 ερωτήσεις</button>
      <button class="size-btn" onclick="startQuiz(${data.total})">🎯 Όλες (${data.total})</button>
    </div>
  `;
}

async function startQuiz(n) {
  const res = await fetch(`/api/start?n=${n}`);
  const data = await res.json();
  state = { questions: data.questions, idx: 0, answers: [], total: data.questions.length };
  showQuestion();
}

function showQuestion() {
  const q = state.questions[state.idx];
  const pct = (state.idx / state.total) * 100;
  const score = state.answers.filter(a => a.correct).length;
  document.getElementById("app").innerHTML = `
    <div class="card">
      <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
      <div class="meta">
        <span>Ερώτηση ${state.idx + 1} / ${state.total}</span>
        <span>Score: ${score}</span>
      </div>
      <div class="qnum">Αρχική #${q.num}</div>
      <div class="qtext">${escapeHtml(q.question)}</div>
      <div class="opt" id="opt-A" onclick="answer('A')"><span class="letter">A</span>ΝΑΙ</div>
      <div class="opt" id="opt-B" onclick="answer('B')"><span class="letter">B</span>ΟΧΙ</div>
      <div id="feedback"></div>
      <button class="next-btn" id="next-btn" onclick="nextQuestion()" style="display:none">
        ${state.idx + 1 < state.total ? "Επόμενη →" : "Αποτέλεσμα →"}
      </button>
    </div>
  `;
}

async function answer(choice) {
  const q = state.questions[state.idx];
  const res = await fetch(`/api/check?num=${q.num}&ans=${choice}`);
  const data = await res.json();
  const isCorrect = data.correct;
  const rightLetter = data.right;

  state.answers.push({ num: q.num, question: q.question, your: choice, right: rightLetter, correct: isCorrect });

  // Visual feedback
  document.getElementById("opt-A").classList.add("disabled");
  document.getElementById("opt-B").classList.add("disabled");
  document.getElementById(`opt-${rightLetter}`).classList.add("correct");
  if (!isCorrect) document.getElementById(`opt-${choice}`).classList.add("wrong");

  const fb = document.getElementById("feedback");
  fb.innerHTML = isCorrect
    ? `<div class="feedback ok">✓ Σωστό!</div>`
    : `<div class="feedback bad">✗ Λάθος. Σωστή: ${rightLetter}. ${OPTIONS[rightLetter]}</div>`;

  document.getElementById("next-btn").style.display = "block";
}

function nextQuestion() {
  state.idx++;
  if (state.idx >= state.total) {
    showResult();
  } else {
    showQuestion();
  }
}

function showResult() {
  const score = state.answers.filter(a => a.correct).length;
  const pct = Math.round((score / state.total) * 100);
  const grade = pct >= 80 ? "🏆" : pct >= 60 ? "👍" : pct >= 40 ? "📖" : "💪";

  const itemsHtml = state.answers.map(a => `
    <div class="result-item ${a.correct ? 'ok' : 'bad'}">
      <div class="result-q">#${a.num}. ${escapeHtml(a.question)}</div>
      <div class="result-a">
        Απάντηση: <span class="${a.correct ? 'label-ok' : 'label-bad'}">${a.your}. ${OPTIONS[a.your]}</span>
        ${!a.correct ? ` — Σωστή: <span class="label-ok">${a.right}. ${OPTIONS[a.right]}</span>` : ''}
      </div>
    </div>
  `).join("");

  document.getElementById("app").innerHTML = `
    <div class="card">
      <h2>${grade} Αποτέλεσμα</h2>
      <div class="score-big">${score}/${state.total}</div>
      <div class="pct">${pct}%</div>
      <button class="restart-btn" onclick="showHome()">🔄 Νέο τεστ</button>
    </div>
    <div class="card">
      <h2>Λεπτομέρειες</h2>
      ${itemsHtml}
    </div>
  `;
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
}

init();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quieter logs
        pass

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, text):
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            return self._html(HTML)

        if path == "/api/info":
            return self._json({"total": len(QUESTIONS)})

        if path == "/api/start":
            try:
                n = int(query.get("n", ["10"])[0])
            except ValueError:
                n = 10
            n = max(1, min(n, len(QUESTIONS)))
            sample = random.sample(QUESTIONS, n)
            # Don't leak correct answers to client
            payload = [{"num": q["num"], "question": q["question"]} for q in sample]
            return self._json({"questions": payload})

        if path == "/api/check":
            try:
                num = int(query.get("num", ["0"])[0])
            except ValueError:
                num = 0
            ans = query.get("ans", [""])[0].upper()
            q = next((x for x in QUESTIONS if x["num"] == num), None)
            if not q:
                return self._json({"error": "not found"}, 404)
            return self._json({
                "correct": ans == q["correct"],
                "right": q["correct"],
            })

        self.send_response(404)
        self.end_headers()


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    if not QUESTIONS:
        print("⚠ Δεν βρέθηκαν ερωτήσεις. Σιγουρέψου ότι το questions.json είναι δίπλα στο app.py")
        return
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print("=" * 55)
    print(f"  🌱 Quiz - GREEN AI ({len(QUESTIONS)} ερωτήσεις)")
    print("=" * 55)
    print(f"  Server στο: http://localhost:{PORT}")
    print(f"  Πάτησε Ctrl+C για έξοδο.")
    print("=" * 55)
    threading.Timer(1.0, open_browser).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Έξοδος. 👋")
        server.shutdown()


if __name__ == "__main__":
    main()
