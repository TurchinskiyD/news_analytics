import feedparser
import hashlib
from datetime import datetime, UTC
import yaml
from pathlib import Path


def load_config():
    config_path = Path(__file__).parents[2] / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()
RSS_FEEDS = config.get("rss_feeds", [])


def hash_id(source, title, url):
    """Генерує унікальний ID на основі джерела + заголовка + URL."""
    return hashlib.sha256(f"{source}_{title}_{url}".encode()).hexdigest()

def fetch_rss_articles():
    articles = []
    fetched_time = datetime.now(UTC).isoformat()

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        source = feed.feed.get("title", "Unknown")

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            published = entry.get("published", None)
            summary = entry.get("summary", "")

            article = {
                "id": hash_id(source, title, link),
                "source": source,
                "category": None,
                "title": title,
                "summary": summary,
                "published_at": published or fetched_time,
                "url": link,
                "language": None,
                "fetched_at": fetched_time,
                # Додаткові аналітичні поля:
                "content_length": len(summary),
                "has_media": "media_content" in entry or "media_thumbnail" in entry,
                "keywords": [],  # буде NLP
                "sentiment": None,  # буде NLP
                "popularity_score": 1,  # буде корисно при deduplication
            }
            articles.append(article)

    return articles


if __name__ == "__main__":
    articles = fetch_rss_articles()
    for a in articles[:2]:  # перші 5 для перегляду
        print(a)
    print(len(articles))
