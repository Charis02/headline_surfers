import os
from typing import List, Dict
import requests

class StoryGenerator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
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
            raise Exception("Error generating story: No articles provided")
            
        # Prepare the context from articles
        context = self._prepare_context(articles)
        
        try:
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
            to guide the avatar's presentation. Make sure to use [PAUSE] between different news topics and 
            [EMPHASIS] for key points or statistics."""

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
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                raise Exception("No content generated in the response")
            
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
        context = ""
        for i, article in enumerate(articles, 1):
            context += f"\n{i}. {article['title']}\n"
            context += f"   {article['content'][:200]}...\n"  # First 200 chars of content
            context += f"   Source: {article['source']}\n"
        
        return context 