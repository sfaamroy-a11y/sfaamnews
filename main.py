"""
main.py - SFAAM NEWS V2
Clean backend - no social media
"""
import logging, os, threading
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from database import get_db, init_db, Article
from scheduler import start_scheduler, run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger   = logging.getLogger(__name__)
SITE_URL = os.getenv("SITE_URL", "https://sfaamnews.com")
REGIONS  = {"world","usa","uk","pakistan","india"}

app = FastAPI(title="SFAAM NEWS")

# Static files
import os as _os
if _os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


class ArticleOut(BaseModel):
    id:           int
    title:        str
    slug:         Optional[str]
    original_url: str
    summary:      Optional[str]
    ai_content:   str
    image_url:    Optional[str]
    region:       str
    meta_desc:    Optional[str]
    keywords:     Optional[str]
    views:        int
    date:         datetime
    class Config:
        from_attributes = True


@app.on_event("startup")
async def startup():
    init_db()
    start_scheduler()
    logger.info("🚀 SFAAM NEWS V2 Live!")


# ── Articles ──────────────────────────────────────────────────
@app.get("/api/articles", response_model=list[ArticleOut])
def list_articles(
    region:   Optional[str] = None,
    page:     int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    q = db.query(Article).order_by(Article.date.desc())
    if region and region in REGIONS:
        q = q.filter(Article.region == region)
    return q.offset((page-1)*per_page).limit(per_page).all()


# ── Single Article ────────────────────────────────────────────
@app.get("/api/articles/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(404, "Not found")
    try:
        a.views = (a.views or 0) + 1
        db.commit()
    except:
        pass
    return a


# ── Search ────────────────────────────────────────────────────
@app.get("/api/search", response_model=list[ArticleOut])
def search(
    q:        str = Query(..., min_length=2),
    page:     int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    term = f"%{q}%"
    return db.query(Article).filter(
        or_(Article.title.ilike(term),
            Article.summary.ilike(term),
            Article.keywords.ilike(term))
    ).order_by(Article.date.desc()).offset((page-1)*per_page).limit(per_page).all()


# ── Stats ─────────────────────────────────────────────────────
@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    total      = db.query(Article).count()
    by_region  = {r: db.query(Article).filter(Article.region==r).count() for r in REGIONS}
    today      = datetime.utcnow().date()
    today_count = db.query(Article).filter(func.date(Article.date)==today).count()
    return {"total": total, "by_region": by_region, "today": today_count}


# ── Newsletter Subscribe ──────────────────────────────────────
@app.post("/api/subscribe")
def subscribe(email: str, db: Session = Depends(get_db)):
    return {"status": "subscribed", "email": email}


# ── Manual Trigger ────────────────────────────────────────────
@app.post("/api/trigger")
def trigger():
    threading.Thread(target=run_pipeline, daemon=True).start()
    return {"status": "Pipeline started."}


# ── Sitemap ───────────────────────────────────────────────────
@app.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    articles = db.query(Article).order_by(Article.date.desc()).limit(1000).all()
    art_urls = "\n".join([f"""  <url>
    <loc>{SITE_URL}/article.html?id={a.id}</loc>
    <lastmod>{a.date.strftime('%Y-%m-%d')}</lastmod>
    <priority>0.8</priority>
  </url>""" for a in articles])
    page_urls = "\n".join([f"""  <url>
    <loc>{SITE_URL}/{p}-news.html</loc>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>""" for p in ["world","usa","uk","pakistan","india"]])
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE_URL}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>
{page_urls}
{art_urls}
</urlset>"""
    return Response(content=xml, media_type="application/xml")


# ── Robots ────────────────────────────────────────────────────
@app.get("/robots.txt")
def robots():
    return Response(
        content=f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml",
        media_type="text/plain"
    )


# ── Frontend ──────────────────────────────────────────────────
@app.get("/{full_path:path}")
async def serve(full_path: str):
    path = f"static/{full_path}" if full_path else "static/index.html"
    if _os.path.exists(path) and _os.path.isfile(path):
        return FileResponse(path)
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",
                host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", 8000)),
                reload=True)
