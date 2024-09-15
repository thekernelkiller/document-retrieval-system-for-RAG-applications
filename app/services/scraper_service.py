import requests
from app.config import Config
from app.services.document_service import add_document
from app.models import Document
import logging

def scrape_news_articles():
    logging.info("Starting to scrape news articles")
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={Config.NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        news = response.json()
        for article in news.get('articles', []):
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            full_text = f"{title}\n{description}\n{content}"
            url = article.get('url', '')
            
            # Check if the article already exists in MongoDB
            if not Document.find_one({'text': full_text}):
                doc_id = add_document(full_text, url)
                logging.info(f"Added new article with ID: {doc_id}")
    else:
        logging.error(f"Failed to fetch news articles. Status code: {response.status_code}")