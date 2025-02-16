import os
from typing import List, Dict
from openai import OpenAI

class StoryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def generate_story(self, articles: List[Dict]) -> str:
        """
        Generate a Gen Z style story from the news articles in Greek.
        
        Args:
            articles (List[Dict]): List of news articles
            
        Returns:
            str: Generated story in Greek Gen Z style
        """
        # Prepare the context from articles
        context = self._prepare_context(articles)
        
        try:
            # Generate the story using GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": """
                    You are a Gen Z content creator who needs to transform formal news into engaging, 
                    casual Greek content for TikTok. Use modern Greek slang, emojis, and Gen Z speaking style. 
                    Keep the content informative but make it sound like a friend telling a story.
                    The story should be around 1-2 minutes when spoken.
                    """},
                    {"role": "user", "content": f"""
                    Here are today's top news articles:
                    {context}
                    
                    Create a compelling story that combines these news items in an engaging way for Greek Gen Z audience.
                    Use appropriate Greek Gen Z slang and style.
                    """}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
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