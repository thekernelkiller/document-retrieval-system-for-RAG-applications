import unittest
from unittest.mock import patch, MagicMock
from pymongo import MongoClient
from app.config import Config
from app.services.scraper_service import scrape_news_articles
from app.models import Document
import time

class TestScheduler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Connect to MongoDB
        cls.client = MongoClient(Config.MONGO_URI)
        cls.db = cls.client['Trademarkia-Document-Retrieval']
        cls.collection = cls.db.documents

    @classmethod
    def tearDownClass(cls):
        # Close MongoDB connection
        cls.client.close()

    @patch('app.services.scraper_service.requests.get')
    def test_scrape_news_articles(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'articles': [
                {
                    'title': 'Test Article 1',
                    'description': 'Description 1',
                    'content': 'Content 1',
                    'url': 'http://example.com/test1'
                },
                {
                    'title': 'Test Article 2',
                    'description': 'Description 2',
                    'content': 'Content 2',
                    'url': 'http://example.com/test2'
                }
            ]
        }
        mock_get.return_value = mock_response

        # Get the initial count of documents
        initial_count = self.collection.count_documents({})

        # Run the scrape_news_articles function
        scrape_news_articles()

        # Wait for a short time to allow for async operations
        time.sleep(2)

        # Get the new count of documents
        new_count = self.collection.count_documents({})

        # Check if new documents were added
        self.assertGreater(new_count, initial_count, "No new documents were added to MongoDB")

        # Check the content of the newly added documents
        new_documents = list(self.collection.find({"url": {"$in": ["http://example.com/test1", "http://example.com/test2"]}}))

        self.assertGreater(len(new_documents), 0, "No new test documents were found")

        # Check the content of each new document
        for doc in new_documents:
            self.assertIn("Test Article", doc['text'], "Test article text not found")
            self.assertIn("http://example.com/test", doc['url'], "Test article URL not found")

        # Clean up: remove the test documents
        self.collection.delete_many({"url": {"$in": ["http://example.com/test1", "http://example.com/test2"]}})

if __name__ == '__main__':
    unittest.main()