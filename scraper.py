"""
scraper.py - SFAAM NEWS V2
5 sources per region = 25 total
All articles credited to SFAAM NEWS only
"""
import feedparser, requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

RSS_SOURCES = {
    "world": [
        {"url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
        {"url": "https://feeds.reuters.com/reuters/topNews"},
        {"url": "https://www.aljazeera.com/xml/rss/all.xml"},
        {"url": "https://rsshub.app/apnews/topics/apf-topnews"},
        {"url": "https://www.theguardian.com/world/rss"},
    ],
    "usa": [
        {"url": "http://rss.cnn.com/rss/edition_us.rss"},
        {"url": "https://moxie.foxnews.com/google-publisher/latest.xml"},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/US.xml"},
        {"url": "https://feeds.washingtonpost.com/rss/national"},
        {"url": "https://rssfeeds.usatoday.com/usatoday-NewsTopStories"},
    ],
    "uk": [
        {"url": "http://feeds.bbci.co.uk/news/uk/rss.xml"},
        {"url": "https://www.theguardian.com/uk/rss"},
        {"url": "https://www.dailymail.co.uk/articles.rss"},
        {"url": "https://www.telegraph.co.uk/rss.xml"},
        {"url": "https://www.independent.co.uk/rss"},
    ],
    "pakistan": [
        {"url": "https://www.dawn.com/feeds/home"},
        {"url": "https://www.geo.tv/rss/1"},
        {"url": "https://arynews.tv/feed/"},
        {"url": "https://www.thenews.com.pk/rss/1/1"},
        {"url": "https://tribune.com.pk/feed/"},
    ],
    "india": [
        {"url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"},
        {"url": "https://feeds.feedburner.com/ndtvnews-top-stories"},
        {"url": "https://www.thehindu.com/feeder/default.rss"},
        {"url": "https://www.indiatoday.in/rss/1206578"},
        {"url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml"},
    ],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_feed(source_url, region):
    try:
        feed   = feedparser.parse(source_url)
        result = []
        for entry in feed.entries[:5]:
            result.append({
                "title":       entry.get("title", ""),
                "url":         entry.get("link", ""),
                "summary":     BeautifulSoup(entry.get("summary",""), "lxml").get_text()[:400],
                "image_url":   _get_image(entry),
                "source_name": "SFAAM NEWS",  # Always SFAAM NEWS
                "region":      region,
            })
        return result
    except Exception as e:
        logger.warning(f"Feed error: {e}")
        return []


def scrape_body(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        for tag in soup(["script","style","nav","footer","aside","header","form"]):
            tag.decompose()
        for sel in ["article","main",".article-body",".story-body",".post-content","#content"]:
            el = soup.select_one(sel)
            if el:
                return el.get_text(separator="\n", strip=True)[:6000]
        return soup.get_text(separator="\n", strip=True)[:6000]
    except Exception as e:
        logger.warning(f"Scrape error: {e}")
        return ""


def get_new_articles(processed_urls):
    new = []
    for region, sources in RSS_SOURCES.items():
        for source in sources:
            for entry in fetch_feed(source["url"], region):
                if entry["url"] and entry["url"] not in processed_urls:
                    body = scrape_body(entry["url"])
                    if body:
                        entry["full_text"] = body
                        new.append(entry)
    logger.info(f"✅ {len(new)} naye articles mile.")
    return new


def _get_image(entry):
    if hasattr(entry,"media_content") and entry.media_content:
        return entry.media_content[0].get("url","")
    if hasattr(entry,"enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type","").startswith("image"):
                return enc.get("href","")
    html = entry.get("summary","")
    if "<img" in html:
        soup = BeautifulSoup(html,"lxml")
        img  = soup.find("img")
        if img: return img.get("src","")
    return ""
