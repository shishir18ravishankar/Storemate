# Storemate 🛒
### Smart AI inventory manager for small retail shops.

Small retail shop owners in India don't use software — they track sales in notebooks, lose records, and deal with losses they can't explain. Storemate fixes that with zero learning curve: just talk to it, photograph your bill, or type a message.

🔗 **Live Demo:** https://storemate-myttr98wahm5xxsnngumxj.streamlit.app

---

## The Problem

Small shop owners manage everything solo — sales, stock, reorders — usually in unorganised sheets or nothing at all. They have no way to track profits, spot trends, or know when to restock. Most software tools are too complex for non-technical users.

## The Solution

Storemate lets shop owners log transactions the way they already communicate — voice notes, photos of bills, or plain text. AI handles the rest: parsing, storing, and generating analysis automatically.

---

## How It Works

1. **Chat tab** — log a sale by typing, speaking, or uploading a photo of a bill
2. **Data Store tab** — all transactions recorded and current stock tracked automatically
3. **Analysis tab** — daily profit, top-selling items, restock alerts, weekly trends

---

## Features

- 🎙️ Voice input — speak your sales naturally ("sold 6 packets of chips")
- 📸 Image upload — photograph a bill or stock sheet, AI extracts the data
- 💬 Text chat — type transactions in plain language
- 📊 Analysis dashboard — profit, loss, top items, trends
- ⚠️ Restock alerts — get notified when stock runs out
- 📦 Inventory tracking — always know what's in stock

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Streamlit (Python) |
| Database | Supabase (PostgreSQL) |
| AI | Groq API — LLaMA 3.3 70B |
| Voice | Speech Recognition |
| Image Processing | AI-based OCR via Groq |

---

## Run Locally

```bash
git clone https://github.com/shishir18ravishankar/Storemate
cd Storemate
pip install -r requirements.txt
```

Create a `.streamlit/secrets.toml` file:
```
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
GROQ_API_KEY = "your_groq_key"
```

```bash
streamlit run app.py
```

---

## Built at BuildWithAI — InnovateX 4.0 Hackathon 2026
Team: Token Burners | Dataset: Sales
