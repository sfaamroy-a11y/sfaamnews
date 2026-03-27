"""
scheduler.py - SFAAM NEWS V2
- News fetch: har 5 min
- Cleanup: midnight
"""
import logging, os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal, Article, ProcessedURL, delete_old_articles
from scraper import get_new_articles
from ai_writer import rewrite_article, make_slug

logger   = logging.getLogger(__name__)
INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "5"))


def run_pipeline():
    logger.info("🔄 News pipeline shuru...")
    db    = SessionLocal()
    saved = 0
    try:
        processed = {r.url for r in db.query(ProcessedURL).all()}
        articles  = get_new_articles(processed)

        for art in articles:
            try:
                result = rewrite_article(
                    art["full_text"],
                    art["title"],
                    art["region"]  # Region-specific key use hogi
                )
                db.add(Article(
                    title        = result["title"],
                    slug         = make_slug(result["title"]),
                    original_url = art["url"],
                    ai_content   = result["body"],
                    summary      = result["meta_desc"][:280],
                    image_url    = art.get("image_url", ""),
                    region       = art["region"],
                    meta_desc    = result["meta_desc"],
                    keywords     = result["keywords"],
                ))
                db.add(ProcessedURL(url=art["url"]))
                db.commit()
                saved += 1
                logger.info(f"  ✅ [{art['region'].upper()}] {result['title'][:50]}")
            except Exception as e:
                db.rollback()
                logger.error(f"  ❌ {e}")
    finally:
        db.close()
    logger.info(f"✅ {saved} naye articles save hue.")


def start_scheduler():
    s = BackgroundScheduler()

    # Har 5 min news fetch
    s.add_job(run_pipeline, IntervalTrigger(minutes=INTERVAL),
              id="fetch_news", replace_existing=True)

    # Raat 12 baje cleanup
    s.add_job(delete_old_articles, CronTrigger(hour=0, minute=0),
              id="cleanup", replace_existing=True)

    s.start()
    logger.info(f"⏰ Scheduler chalu — har {INTERVAL} minute mein news.")
    return s
