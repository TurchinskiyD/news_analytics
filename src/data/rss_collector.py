import logging
import time
import feedparser
import hashlib
from datetime import datetime, UTC

import requests
import yaml
from pathlib import Path


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


def hash_id(source, title, url):
    """Генерує унікальний ID на основі джерела + заголовка + URL."""
    return hashlib.sha256(f"{source}_{title}_{url}".encode()).hexdigest()


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


if __name__ == "__main__":
    start_time = time.time()
    project_root = Path(__file__).parents[2]

    # Створення папки логів
    log_path = project_root / "logs"
    log_path.mkdir(exist_ok=True)

    # Основний лог-файл
    log_file = log_path / "rss_collector.log"
    failed_sources_file = log_path / "failed_sources.txt"

    # Налаштування логування (файл + консоль)
    logger = logging.getLogger("rss_logger")
    logger.setLevel(logging.INFO)

    # Файл
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)

    # Консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

    # Отримання статей
    rss_articles, rss_ok, rss_failed = fetch_rss_articles()
    gnews_articles, gnews_ok, gnews_failed = fetch_gnews_top10_articles()

    if gnews_ok:
        logger.info("🟢 GNews API: successfully fetched top 10 articles")
    else:
        logger.warning("🔴 GNews API: failed to fetch articles")

    for a in gnews_articles[:2]:  # попередній перегляд новин GNews
        logger.info(f"GNews article: {a['title']} | {a['url']}")


    articles = rss_articles + gnews_articles
    success_sources = rss_ok + gnews_ok
    failed_sources = rss_failed + gnews_failed

    duration = round(time.time() - start_time, 2)

    # Логування результатів
    logger.info("✅ RSS collection finished")
    logger.info(f"✅ Sources processed: {success_sources}/{len(RSS_FEEDS)}")
    logger.info(f"📰 Total articles collected: {len(articles)}")
    logger.info(f"⏱ Duration: {duration} seconds")

    if failed_sources:
        logger.warning(f"⚠️ Failed sources: {len(failed_sources)}")
        # Пишемо в файл биті джерела
        with open(failed_sources_file, "w", encoding="utf-8") as f:
            for url, err in failed_sources:
                timestamp = datetime.now(UTC).isoformat()
                line = f"{timestamp} [WARNING] ⚠️ Failed source: {url} | Reason: {err}\n"
                logger.warning(line.strip())
                f.write(line)


    for a in articles[:2]:  # перші 2 для перегляду
        print(a)
    print(len(articles))
