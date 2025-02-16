import os
from typing import List, Dict
from datetime import datetime
import feedparser
import requests

class NewsFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.max_articles = int(os.getenv('MAX_ARTICLES', 10))
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        # Define RSS feed sources
        self.sources = {
            'cyprus_mail': {
                'url': 'https://cyprus-mail.com/feed/',
                'language': 'el'
            },
            'in_cyprus': {
                'url': 'https://in-cyprus.philenews.com/feed/',
                'language': 'el'
            },
            'kathimerini_en': {
                'url': 'https://www.ekathimerini.com/rss/',
                'language': 'el'
            }
        }
    
    def fetch_articles(self, date: str) -> List[Dict]:
        """
        Fetch top Greek news articles for the specified date.
        
        Args:
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            List[Dict]: List of articles with title and content
        """
        try:
            # Convert date string to datetime for comparison
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Fetch articles from all sources
            articles = self._fetch_from_rss(target_date)
            
            if not articles:
                raise Exception(f"No articles found for date {date}")
            
            # Rank articles by importance
            ranked_articles = self._rank_articles(articles)
            
            # Return top N articles
            return ranked_articles[:self.max_articles]
            
        except Exception as e:
            raise Exception(f"Error fetching news articles: {str(e)}")
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string from various formats used by different RSS feeds.
        
        Args:
            date_str (str): Date string from RSS feed
            
        Returns:
            datetime: Parsed datetime object
        """
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # Standard RSS format
            '%Y-%m-%dT%H:%M:%S%z',       # ISO format with timezone
            '%Y-%m-%dT%H:%M:%S+%z',      # ISO format with + timezone
            '%Y-%m-%d %H:%M:%S',         # Simple format
            '%a, %d %b %Y %H:%M:%S GMT', # GMT format
            '%Y-%m-%dT%H:%M:%SZ'         # UTC format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        # If no format matches, try parsing with dateutil
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            print(f"Could not parse date: {date_str}")
            return datetime.now()  # Return current time as fallback
    
    def _fetch_from_rss(self, target_date) -> List[Dict]:
        """
        Fetch articles from RSS feeds for the target date.
        
        Args:
            target_date: Date to fetch articles for
            
        Returns:
            List[Dict]: List of articles
        """
        all_articles = []
        
        for source_id, source_info in self.sources.items():
            try:
                print(f"Fetching from {source_id}...")
                feed = feedparser.parse(source_info['url'])
                
                if feed.get('status', 0) == 404:
                    print(f"Error: Feed not found for {source_id}")
                    continue
                    
                for entry in feed.entries:
                    try:
                        # Get published date from various possible fields
                        date_str = entry.get('published', entry.get('updated', entry.get('pubDate')))
                        if not date_str:
                            continue
                            
                        # Parse the publication date
                        pub_date = self._parse_date(date_str).date()
                        
                        # Skip if not from target date
                        if pub_date != target_date:
                            continue
                        
                        # Extract content (try different fields as feeds vary)
                        content = ''
                        if hasattr(entry, 'content'):
                            content = entry.content[0].value
                        elif hasattr(entry, 'summary'):
                            content = entry.summary
                        elif hasattr(entry, 'description'):
                            content = entry.description
                            
                        article = {
                            'title': entry.title,
                            'content': content,
                            'url': entry.link,
                            'source': source_id,
                            'category': self._detect_category(entry.title, content),
                            'published': date_str
                        }
                        
                        all_articles.append(article)
                        
                    except (AttributeError, ValueError) as e:
                        print(f"Error processing article from {source_id}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error fetching from {source_id}: {str(e)}")
                continue
        
        print(f"Found {len(all_articles)} articles for {target_date}")
        return all_articles
    
    def _detect_category(self, title: str, description: str) -> str:
        """
        Detect article category based on title and description.
        
        Args:
            title (str): Article title
            description (str): Article description
            
        Returns:
            str: Detected category
        """
        # Common Greek news categories and their keywords
        categories = {
            'politics': ['politic', 'government', 'parliament', 'minister', 'election'],
            'economy': ['econom', 'business', 'bank', 'finance', 'market'],
            'society': ['health', 'education', 'work', 'social'],
            'world': ['world', 'international', 'global', 'foreign'],
            'sports': ['sport', 'football', 'basketball', 'game']
        }
        
        text = (title + ' ' + (description or '')).lower()
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
                
        return 'general'
    
    def _rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Rank articles by importance using Gemini.
        
        Args:
            articles (List[Dict]): List of articles to rank
            
        Returns:
            List[Dict]: Ranked list of articles
        """
        try:
            # Prepare articles for ranking
            articles_text = "\n\n".join([
                f"Article {i}:\nTitle: {article['title']}\nCategory: {article['category']}\nContent: {article['content'][:200]}..."
                for i, article in enumerate(articles)
            ])
            
            prompt = """You are an article ranking system. Your task is to analyze the given news articles and rank them by importance.
            Consider these factors:
            1. Impact on Cypriot and Greek society
            2. Urgency of the news
            3. Public interest
            4. Long-term significance
            5. Relevance to young audiences

            IMPORTANT: You must ONLY return a comma-separated list of article numbers (0-based indices).
            For example, if Article 2 is most important, followed by Article 5, then Article 1, etc., you should return:
            2,5,1,3,0,4

            DO NOT include any other text, explanations, or formatting in your response.
            ONLY return the comma-separated numbers."""

            # Make the API request
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json={
                    "contents": [{
                        "parts":[{
                            "text": articles_text + "\n\n" + prompt
                        }]
                    }],
                    "safety_settings": {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    },
                    "generation_config": {
                        "temperature": 0.1,  # Lower temperature for more deterministic output
                        "max_output_tokens": 100,  # Reduced as we only need a short response
                        "top_p": 0.8,
                        "top_k": 40
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract and validate the generated text
            if 'candidates' in result and len(result['candidates']) > 0:
                ranked_indices_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up the response - remove any non-numeric characters except commas
                cleaned_indices = ''.join(char for char in ranked_indices_text if char.isdigit() or char == ',')
                if not cleaned_indices:
                    raise ValueError("No valid indices found in API response")
                
                # Parse the response to get ordered indices
                try:
                    ranked_indices = [int(idx.strip()) for idx in cleaned_indices.split(',') if idx.strip()]
                    
                    # Validate indices
                    valid_indices = [idx for idx in ranked_indices if 0 <= idx < len(articles)]
                    if not valid_indices:
                        raise ValueError("No valid article indices found")
                    
                    # Reorder articles based on ranking
                    ranked_articles = [articles[idx] for idx in valid_indices]
                    
                    # If some articles weren't ranked, append them at the end
                    unranked_indices = set(range(len(articles))) - set(valid_indices)
                    ranked_articles.extend(articles[idx] for idx in unranked_indices)
                    
                    return ranked_articles
                except ValueError as e:
                    raise ValueError(f"Failed to parse indices: {str(e)}")
            else:
                raise Exception("No content generated in the response")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error ranking articles: API request failed - {str(e)}")
        except Exception as e:
            raise Exception(f"Error ranking articles: {str(e)}") 