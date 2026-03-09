"""
Placeholder for RSS feed scraping.
Will implement with feedparser.
"""
import feedparser

from .models import NewsArticle


def fetch_rss_feeds():
    """
    Fetch from configured RSS sources and store new articles.
    """
    sources = [
        'http://feeds.bbci.co.uk/news/world/middle_east/rss.xml',
        # add more
    ]
    for url in sources:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # deduplicate by link
            article, created = NewsArticle.objects.get_or_create(
                url=entry.link,
                defaults={
                    'source': 'BBC',
                    'title': entry.title,
                    'published_at': entry.published,
                    'content': entry.summary,
                }
            )
    return f"Fetched from {len(sources)} sources"