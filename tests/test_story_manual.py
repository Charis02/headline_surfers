import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.story_generator import StoryGenerator
from test_story_generator import SAMPLE_ARTICLES

def main():
    # Load environment variables
    load_dotenv()
    
    # Create story generator
    generator = StoryGenerator()
    
    # Generate story
    print("\n=== Input Articles ===")
    for i, article in enumerate(SAMPLE_ARTICLES, 1):
        print(f"\n{i}. {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Content: {article['content'][:100]}...")  # Show first 100 chars
    
    print("\n=== Generated Story ===")
    try:
        story = generator.generate_story(SAMPLE_ARTICLES)
        print("\n" + story + "\n")
    except Exception as e:
        print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    main() 