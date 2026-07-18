import os, json, asyncio, logging, textwrap
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("vows-agent")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY", "placeholder")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

app = FastAPI(title="vows agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

async def ask_deepseek(prompt: str, system: str = "You are a helpful assistant.", temperature: float = 0.7) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(DEEPSEEK_URL, json={
            "model": "deepseek-v4-flash",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": temperature, "max_tokens": 4096
        }, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"})
        if r.status_code != 200:
            raise HTTPException(503, f"DeepSeek error: {r.status_code} {r.text}")
        return r.json()["choices"][0]["message"]["content"]

def send_telegram(msg: str):
    if not TELEGRAM_TOKEN: return
    asyncio.create_task(_send_tg(msg))

async def _send_tg(msg: str):
    try:
        async with httpx.AsyncClient() as c:
            await c.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
                "chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"
            })
    except Exception as e:
        log.error(f"tg send failed: {e}")

@app.get("/api/health")
async def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat(), "brand": "vows"}

@app.get("/api/analyze-competitors")
async def analyze_competitors():
    log.info("analyzing competitors...")
    resp = await ask_deepseek(
        "Analyze the visual identity, website structure, and key design patterns of these streetwear brands: "
        "Stüssy, Off-White, Marcelo Miracle, Rhude, Aimé Leon Dore. "
        "Focus on: layout, typography, color palette, product presentation, navigation style, overall vibe. "
        "Give me a short structured analysis (in Russian, 2-3 sentences per brand).",
        system="You are a streetwear brand strategist and web designer."
    )
    log.info(f"analysis done ({len(resp)} chars)")
    return {"analysis": resp}

@app.get("/api/scenario/today")
async def scenario_today():
    log.info("generating today script...")
    resp = await ask_deepseek(
        "Generate a short, trendy script for a TikTok/Instagram Reel about streetwear clothing. "
        "The brand is 'vows' (pronounced 'vows', reads like 'low-see'). "
        "It's a young streetwear brand. Current product: waffle material long sleeve, loose crop fit. "
        "The script should be for a 30-second video, include camera angles and text overlay ideas. "
        "Write in Russian. Make it viral, focus on aesthetic and vibe. Include 3 hooks in the beginning.",
        system="You are a TikTok content strategist who creates viral fashion content."
    )
    return {"date": datetime.now().strftime("%Y-%m-%d"), "script": resp}

@app.post("/api/scenario/custom")
async def scenario_custom(prompt: str):
    resp = await ask_deepseek(
        f"Generate a detailed TikTok/Reels script for a streetwear brand based on this request: {prompt}",
        system="You are a viral fashion content creator. Write in Russian. Include camera angles, text overlays, and sound suggestions."
    )
    return {"script": resp}

@app.post("/api/generate-description")
async def generate_description(item: str):
    resp = await ask_deepseek(
        f"Write a stylish product description for a streetwear item: {item}. "
        "Make it sound premium and minimal. Max 3 sentences. In Russian. "
        "Focus on material, fit, vibe. Avoid clichés.",
        system="You are a copywriter for a high-end streetwear brand."
    )
    return {"description": resp}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3001)
