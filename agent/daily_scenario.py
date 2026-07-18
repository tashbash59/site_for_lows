import os, sys, json, asyncio, httpx, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("daily-scenario")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY", "placeholder")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "placeholder")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

async def main():
    log.info("Generating daily scenario...")
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post("https://api.deepseek.com/chat/completions", json={
            "model": "deepseek-v4-flash",
            "messages": [
                {"role": "system", "content": "You are a viral TikTok content strategist for a streetwear brand."},
                {"role": "user", "content": (
                    "Generate a script for a 30-second TikTok/Reel for the streetwear brand 'vows'. "
                    "Product: waffle material long sleeve, loose crop fit. "
                    "Date: " + datetime.now().strftime("%Y-%m-%d") + ". "
                    "Include: 3 hooks, camera angles, text overlays, sound suggestion. "
                    "Make it trendy and viral. Write in Russian."
                )}
            ],
            "temperature": 0.9,
            "max_tokens": 2048
        }, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"})
        if r.status_code != 200:
            log.error(f"DeepSeek error: {r.status_code}")
            return
        scenario = r.json()["choices"][0]["message"]["content"]
        log.info(f"Scenario generated ({len(scenario)} chars)")

    msg = f"<b>vows — daily scenario</b>\n<code>{datetime.now().strftime('%Y-%m-%d %H:%M')}</code>\n\n{scenario}"
    print(msg)

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        async with httpx.AsyncClient() as c:
            await c.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={
                "chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"
            })
        log.info("Sent to Telegram")
    else:
        log.warning("No TELEGRAM_CHAT_ID set — printed to stdout")

if __name__ == "__main__":
    asyncio.run(main())
