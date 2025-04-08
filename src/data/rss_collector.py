import json
import time
import feedparser
import hashlib
from datetime import datetime, UTC

import requests
import yaml
from pathlib import Path
from src.utils.logger import setup_logger, log_collection_results


def load_config():
    base_path = Path(__file__).parents[2]
    config_path = base_path / "config" / "config.yaml"
    secret_path = base_path / "config" / "secret_config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if secret_path.exists():
         with open(secret_path, 'r', encoding='utf-8') as f:
             secrets = yaml.safe_load(f)
         config.update(secrets)

    return config


config = load_config()
RSS_FEEDS = config.get("rss_feeds", [])


def hash_id(source, title, url, length=10):
    """
    Генерує скорочений унікальний ID на основі джерела + заголовка + URL.
    За замовчуванням — 10 символів (перші символи SHA-256).
    """
    full_hash = hashlib.sha256(f"{source}_{title}_{url}".encode()).hexdigest()
    return full_hash[:length]


def fetch_rss_articles():
    articles = []
    success_sources = 0
    failed_sources = []
    fetched_time = datetime.now(UTC).isoformat()

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                raise ValueError(f"Feed parsing error: {feed.bozo_exception}")

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

            success_sources += 1

        except Exception as e:
            failed_sources.append((url, str(e)))

    return articles, success_sources, failed_sources


def fetch_gnews_top10_articles():
    api_key = config.get("gnews_api_key")
    lang = config.get("gnews_lang", "en")
    country = config.get("gnews_country", "us")
    category = config.get("gnews_category", "general")
    url = f"https://gnews.io/api/v4/top-headlines?category={category}&lang={lang}&country={country}&max=10&apikey={api_key}"

    articles = []
    fetched_time = datetime.now(UTC).isoformat()

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for item in data.get("articles", []):
            title = item.get("title", "")
            link = item.get("url", "")
            published = item.get("publishedAt", fetched_time)
            summary = item.get("description", "")

            article = {
                "id": hash_id("GNews", title, link),
                "source": item.get("source", {}).get("name", "GNews"),
                "category": category,
                "title": title,
                "summary": summary,
                "published_at": published,
                "url": link,
                "language": lang,
                "fetched_at": fetched_time,
                "content_length": len(summary),
                "has_media": item.get("image") is not None,
                "keywords": [],
                "sentiment": None,
                "popularity_score": 1,
            }
            articles.append(article)

        return articles, 1, []

    except Exception as e:
        return [], 0, [("GNews API", str(e))]


def save_articles_to_raw(articles, raw_dir_name="data/raw"):
    raw_path = Path(__file__).parents[2] / raw_dir_name
    raw_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"news_{timestamp}.json"
    file_path = raw_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    return file_path


if __name__ == "__main__":

    if __name__ == "__main__":
        start_time = time.time()
        logger, log_path = setup_logger()
        failed_sources_file = log_path / "failed_sources.txt"

        rss_articles, rss_ok, rss_failed = fetch_rss_articles()
        gnews_articles, gnews_ok, gnews_failed = fetch_gnews_top10_articles()
        duration = round(time.time() - start_time, 2)

        articles = rss_articles + gnews_articles  # ⬅ об'єднання повертаємо сюди
        failed_sources = rss_failed + gnews_failed
        success_sources = rss_ok + gnews_ok

        log_collection_results(
        logger=logger,
        rss_ok=rss_ok,
        gnews_ok=gnews_ok,
        failed_sources=failed_sources,
        articles=articles,
        gnews_articles=gnews_articles,
        duration=duration,
        rss_feeds_len=len(RSS_FEEDS),
        failed_sources_file_path=failed_sources_file
        )

        saved_path = save_articles_to_raw(articles)

        logger.info(f"💾 Articles saved to: {saved_path}")

        for a in articles[:2]:
            print(a)
        print(len(articles))
