from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.scraper_service import scrape_news_articles
from app.api.routes import api_bp
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/document_retrieval.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Document Retrieval startup')

    # Register the blueprint with a URL prefix
    app.register_blueprint(api_bp, url_prefix='/api')

    # Set up the background scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(scrape_news_articles, 'interval', hours=1)
    scheduler.start()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)