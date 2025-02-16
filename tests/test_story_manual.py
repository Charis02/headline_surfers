import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.story_generator import StoryGenerator
from test_story_generator import SAMPLE_ARTICLES

# Load environment variables
from dotenv import load_dotenv
import os


def validate_story(story: str) -> tuple[bool, list[str]]:
    """Validate the generated story meets all requirements"""
    issues = []
    
    # Check story length
    words = len(story.split())
    if not (150 <= words <= 450):
        issues.append(f"Story length ({words} words) is outside target range (150-450)")
    
    # Check for emotion markers
    required_markers = {
        '[PAUSE]': 'Story must include [PAUSE] between topics',
        '[EMPHASIS]': 'Story should include emphasized points',
        '[EXCITED]': 'Story should include excited moments',
        '[SERIOUS]': 'Story should include serious tone for news',
        '[THINKING]': 'Story should include analytical moments',
    }
    
    found_markers = []
    for marker in required_markers:
        if marker in story:
            found_markers.append(marker)
    
    if len(found_markers) < 3:
        issues.append(f"Found only {len(found_markers)} markers, minimum required is 3")
    
    # Check for Greek text
    if not any(char in story for char in 'αβγδεζηθικλμνξοπρστυφχψω'):
        issues.append("Story doesn't contain Greek text")
    
    # Check category-specific markers
    categories_present = set(article['category'] for article in SAMPLE_ARTICLES)
    if 'economy' in categories_present and '[SERIOUS]' not in story:
        issues.append("Economic news should have [SERIOUS] marker")
    if 'technology' in categories_present and '[EXCITED]' not in story:
        issues.append("Technology news should have [EXCITED] marker")
    if any('95%' in article['content'] for article in SAMPLE_ARTICLES) and '[THINKING]' not in story:
        issues.append("Articles with statistics should have [THINKING] marker")
    
    return len(issues) == 0, issues

def analyze_story(story: str) -> None:
    """Analyze and print statistics about the generated story"""
    print("\n=== Story Analysis ===")
    
    # Word count
    words = len(story.split())
    print(f"Word count: {words} words")
    print(f"Speaking time (approx): {words/150:.1f} minutes")
    
    # Emotion markers
    all_markers = ['[PAUSE]', '[EMPHASIS]', '[EXCITED]', '[SERIOUS]', 
                  '[CURIOUS]', '[SMILE]', '[THINKING]']
    marker_counts = {marker: story.count(marker) for marker in all_markers}
    
    print("\nEmotion Markers:")
    for marker, count in marker_counts.items():
        print(f"  {marker}: {count} times")
    
    # Category coverage
    categories = set(article['category'] for article in SAMPLE_ARTICLES)
    print("\nInput Categories:", ', '.join(categories))
    
    # Statistics
    print("\nStatistics:")
    print(f"  Total markers: {sum(marker_counts.values())}")
    print(f"  Unique markers: {sum(1 for count in marker_counts.values() if count > 0)}")
    print(f"  Most used marker: {max(marker_counts.items(), key=lambda x: x[1])[0]}")

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print("\n❌ Error: GEMINI_API_KEY environment variable is not set")
        return
    
    # Create story generator
    generator = StoryGenerator(api_key=GEMINI_API_KEY)
    
    # Print input articles
    print("\n=== Input Articles ===")
    for i, article in enumerate(SAMPLE_ARTICLES, 1):
        print(f"\n{i}. {article['title']}")
        print(f"Category: {article['category']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published']}")
        print(f"Content: {article['content'][:100]}...")  # Show first 100 chars
    
    # Generate and validate story
    print("\n=== Generated Story ===")
    try:
        story = generator.generate_story(SAMPLE_ARTICLES)
        print("\n" + story + "\n")
        
        # Validate story
        is_valid, issues = validate_story(story)
        if not is_valid:
            print("\n⚠️ Story Validation Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ Story meets all requirements")
        
        # Analyze story
        analyze_story(story)
        
    except Exception as e:
        print(f"\n❌ Error generating story: {str(e)}\n")

if __name__ == "__main__":
    main() 