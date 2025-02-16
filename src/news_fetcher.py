import os
from typing import List, Dict
from datetime import datetime
from newsapi import NewsApiClient
from google.cloud import translate_v2 as translate

class NewsFetcher:
    def __init__(self):
        self.news_api = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        self.translator = translate.Client()
        self.max_articles = int(os.getenv('MAX_ARTICLES', 10))
    
    def fetch_articles(self, date: str) -> List[Dict]:
        """
        Fetch top Greek news articles for the specified date.
        
        Args:
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            List[Dict]: List of articles with title and content
        """
        try:
            # Convert date string to datetime
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # Fetch articles from NewsAPI
            response = self.news_api.get_everything(
                q='',  # Empty query to get all news
                language='el',  # Greek language
                from_param=date,
                to=date,
                sort_by='relevancy',
                page_size=self.max_articles
            )
            
            if not response['articles']:
                raise Exception(f"No articles found for date {date}")
            
            # Process and translate articles if needed
            processed_articles = []
            for article in response['articles'][:self.max_articles]:
                # Skip articles without content
                if not article.get('content') or not article.get('title'):
                    continue
                    
                processed_article = {
                    'title': article['title'],
                    'content': article['content'],
                    'url': article['url'],
                    'source': article['source']['name']
                }
                
                processed_articles.append(processed_article)
            
            if not processed_articles:
                raise Exception("No valid articles found after processing")
                
            return processed_articles
            
        except Exception as e:
            raise Exception(f"Error fetching news articles: {str(e)}")
    
    def _translate_text(self, text: str, target_language: str = 'el') -> str:
        """
        Translate text to target language if not already in that language.
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (default: 'el' for Greek)
            
        Returns:
            str: Translated text
        """
        try:
            result = self.translator.translate(text, target_language=target_language)
            return result['translatedText']
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            return text  # Return original text if translation fails 