# Quiz - Τράπεζα Θεμάτων GREEN AI & Βιώσιμη Καινοτομία

50 ερωτήσεις ΝΑΙ/ΟΧΙ. Δύο τρόποι εκτέλεσης:

## 1) Online — Replit / Google Colab (CLI version)

Ανέβασε τα αρχεία `quiz_cli.py` και `questions.json`. Τρέξε:

```
python quiz_cli.py
```

## 2) Web app στο Vercel (Flask)

### Τοπική δοκιμή
```
pip install -r requirements.txt
python api/index.py
```
Άνοιξε http://localhost:5000

### Deploy στο Vercel
1. Κάνε push το repo στο GitHub.
2. Στο vercel.com → New Project → import το repo.
3. Vercel ανιχνεύει αυτόματα Python μέσω `vercel.json`.
4. (Προαιρετικό) Set environment variable `SECRET_KEY` σε τυχαία τιμή.

Ή μέσω CLI:
```
npm i -g vercel
vercel
```

## Δομή
- `questions.json` — η βάση 50 ερωτήσεων (`num`, `question`, `correct`)
- `quiz_cli.py` — CLI version
- `api/index.py` — Flask web app
- `vercel.json` — Vercel config
- `requirements.txt` — Python dependencies
