# Starlette compatibility shim for modern Starlette releases
try:
    import starlette.routing
    _orig = starlette.routing.Router.__init__
    starlette.routing.Router.__init__ = lambda self, *a, on_startup=None, on_shutdown=None, **kw: _orig(self, *a, **kw)
    import fastapi
    if not hasattr(fastapi.FastAPI, "max_body_size"):
        fastapi.FastAPI.max_body_size = None
except Exception:
    pass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import base64
import asyncio
import httpx
from bs4 import BeautifulSoup
import os

app = FastAPI(title="Obscura Stealth Headless Browser")

class NavigateRequest(BaseModel):
    url: str
    take_screenshot: bool = True
    timeout_ms: int = 20000

class ScreenshotRequest(BaseModel):
    url: str
    full_page: bool = True

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "obscura_stealth_browser"}

@app.post("/navigate")
async def navigate(req: NavigateRequest):
    """
    Navigates to the specified URL using Playwright with stealth evasions.
    Extracts text, metadata, and captures full-page screenshot.
    """
    url = req.url
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # Try Playwright with stealth
    try:
        from playwright.async_api import async_playwright
        from playwright_stealth import stealth_async

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu"
                ]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await stealth_async(page)
            
            await page.goto(url, timeout=req.timeout_ms, wait_until="domcontentloaded")
            await page.wait_for_timeout(1000)

            title = await page.title()
            content = await page.content()
            
            # Extract clean readable text
            soup = BeautifulSoup(content, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg"]):
                tag.decompose()
            text_preview = " ".join(soup.get_text().split())[:1500]

            screenshot_b64 = None
            if req.take_screenshot:
                screenshot_bytes = await page.screenshot(full_page=False)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            await browser.close()
            return {
                "success": True,
                "url": url,
                "title": title,
                "text_preview": text_preview,
                "screenshot_base64": screenshot_b64,
                "engine": "playwright_stealth"
            }
    except Exception as e:
        # Fallback to HTTP extraction if Playwright browser dependencies are not available in local test env
        print(f"[Obscura] Playwright execution error, falling back to httpx: {e}")
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NemoClaw/1.0"}
                resp = await client.get(url, headers=headers)
                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.title.string if soup.title else url
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()
                text_preview = " ".join(soup.get_text().split())[:1500]
                
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "text_preview": text_preview,
                    "screenshot_base64": None,
                    "engine": "httpx_fallback",
                    "note": f"Playwright fallback: {str(e)}"
                }
        except Exception as http_err:
            raise HTTPException(status_code=500, detail=f"Failed to fetch {url}: {str(http_err)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
