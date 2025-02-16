import os
from typing import List, Dict
import requests

class StoryGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        print(f"API key: {self.api_key}")
    def generate_story(self, articles: List[Dict]) -> str:
        """
        Generate a Gen Z style story from the news articles in Greek.
        
        Args:
            articles (List[Dict]): List of news articles
            
        Returns:
            str: Generated story in Greek Gen Z style
            
        Raises:
            Exception: If articles list is empty or if there's an error generating the story
        """
        if not articles:
            raise Exception("No articles provided")
            
        try:
            # Validate article structure
            required_fields = ['title', 'content', 'source', 'category', 'published', 'url']
            for article in articles:
                missing_fields = [field for field in required_fields if field not in article]
                if missing_fields:
                    raise Exception(f"Error generating story: Missing required fields {missing_fields} in article")
            
            # Prepare the context from articles
            context = self._prepare_context(articles)
            
            prompt = """You are a Gen Z content creator who needs to transform formal news into engaging, 
            casual Greek content for a digital avatar to present. Use modern Greek slang, emojis, and Gen Z speaking style. 
            Keep the content informative but make it sound like a friend telling a story.
            The story should be around 1-2 minutes when spoken.

            Use the following markers in the text:
            - [PAUSE] for natural pauses between topics
            - [EMPHASIS] for words that should be emphasized
            - [EXCITED] for excited tone
            - [SERIOUS] for serious tone
            - [CURIOUS] for curious/questioning tone
            - [SMILE] for moments where the avatar should smile
            - [THINKING] for contemplative moments

            Here are today's top news articles:
            """ + context + """
            
            Create a compelling story that combines these news items in an engaging way for Greek Gen Z audience.
            Use appropriate Greek Gen Z slang and style. Include the emotion markers naturally throughout the text
            to guide the avatar's presentation.
            
            The story MUST:
            1. Include at least 3 emotion markers
            2. Be between 150-450 words long
            3. Use [SERIOUS] for political/economic news
            4. Use [EXCITED] for positive developments
            5. Use [THINKING] for analysis/statistics
            6. Include [PAUSE] between topics
            7. Use [EMPHASIS] for key points or statistics"""
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json={
                    "contents": [{
                        "parts":[{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1000,
                    }
                }
            )
            
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            
            # Extract the generated text from the response
            if 'candidates' in result and len(result['candidates']) > 0:
                story = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Verify story meets requirements
                if not any(marker in story for marker in ['[PAUSE]', '[EMPHASIS]', '[EXCITED]', '[SERIOUS]', '[CURIOUS]', '[SMILE]', '[THINKING]']):
                    raise Exception("Error generating story: Generated content does not contain required emotion markers")
                    
                words = len(story.split())
                if not (150 <= words <= 450):
                    raise Exception(f"Error generating story: Generated content length ({words} words) is outside target range (150-450 words)")
                    
                return story
            else:
                raise Exception("Error generating story: No content generated in the response")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error generating story: API request failed - {str(e)}")
        except KeyError as e:
            raise Exception(f"Error generating story: Missing required field {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating story: {str(e)}")
    
    def _prepare_context(self, articles: List[Dict]) -> str:
        """
        Prepare the context string from the articles.
        
        Args:
            articles (List[Dict]): List of news articles
            
        Returns:
            str: Formatted context string
        """
        try:
            context = ""
            for i, article in enumerate(articles, 1):
                context += f"\n{i}. {article['title']}\n"
                context += f"   Category: {article['category']}\n"
                context += f"   {article['content'][:200]}...\n"  # First 200 chars of content
                context += f"   Source: {article['source']}\n"
            
            return context
            
        except KeyError as e:
            raise Exception(f"Error preparing context: Missing required field {str(e)}")
        except Exception as e:
            raise Exception(f"Error preparing context: {str(e)}") 