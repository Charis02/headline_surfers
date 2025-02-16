import os
import pytest
from datetime import datetime
from src.news_fetcher import NewsFetcher
from src.story_generator import StoryGenerator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def news_fetcher():
    """Create a NewsFetcher instance"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable not set")
    return NewsFetcher(api_key=api_key)

@pytest.fixture
def story_generator():
    """Create a StoryGenerator instance"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable not set")
    return StoryGenerator(api_key=api_key)

@pytest.mark.integration
def test_news_to_story_pipeline(news_fetcher, story_generator):
    """Test the complete pipeline from news fetching to story generation"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch articles
        articles = news_fetcher.fetch_articles(today)
        assert len(articles) > 0, "No articles found"
        
        # Generate story
        story = story_generator.generate_story(articles)
        assert isinstance(story, str), "Generated story should be a string"
        assert len(story) > 0, "Generated story should not be empty"
        
        # Check for emotion markers
        emotion_markers = ["[SERIOUS]", "[EMPHASIS]", "[CULTURAL]", "[CALL_TO_ACTION]"]
        marker_count = sum(1 for marker in emotion_markers if marker in story)
        assert marker_count > 0, "Story should contain at least one emotion marker"
        
    except Exception as e:
        pytest.fail(f"Pipeline test failed: {str(e)}")

@pytest.fixture(autouse=True)
def load_env():
    """Debug fixture to print environment information"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    # Parse the .env file manually
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                key = line.split('=', 1)[1].strip()
                os.environ['GEMINI_API_KEY'] = key
                break
    
    # Remove the debug prints if you don't need them anymore
    # print(f"Environment: GEMINI_API_KEY={os.getenv('GEMINI_API_KEY')}")

@pytest.mark.integration
def test_full_pipeline_with_specific_category(news_fetcher, story_generator):
    """Test pipeline with articles from a specific category"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch articles
        all_articles = news_fetcher.fetch_articles(today)
        assert len(all_articles) > 0, "No articles found"
        
        # Filter for specific category
        politics_articles = [a for a in all_articles if a['category'] == 'politics']
        if not politics_articles:
            pytest.skip("No politics articles found for testing")
        
        # Generate story from politics articles
        story = story_generator.generate_story(politics_articles)
        assert isinstance(story, str), "Generated story should be a string"
        assert len(story) > 0, "Generated story should not be empty"
        
    except Exception as e:
        pytest.fail(f"Category-specific pipeline test failed: {str(e)}")

@pytest.mark.integration
def test_error_handling_and_recovery(news_fetcher, story_generator):
    """Test error handling and recovery in the pipeline"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch articles
        articles = news_fetcher.fetch_articles(today)
        assert len(articles) > 0, "No articles found for testing"
        
        # Test with invalid articles structure
        with pytest.raises(Exception) as exc_info:
            story_generator.generate_story([{'invalid': 'article'}])
        assert "Missing required fields" in str(exc_info.value)
        
        # Test with empty article list
        with pytest.raises(Exception) as exc_info:
            story_generator.generate_story([])
        assert "No articles provided" in str(exc_info.value)
        
        # Test successful recovery
        story = story_generator.generate_story(articles[:2])  # Limit to 2 articles
        assert isinstance(story, str)
        assert len(story) > 0
        
    except Exception as e:
        pytest.fail(f"Unexpected error in error handling test: {str(e)}")

@pytest.mark.integration
def test_story_length_and_speaking_time(news_fetcher, story_generator):
    """Test that generated stories meet length and speaking time requirements"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch articles
        articles = news_fetcher.fetch_articles(today)
        assert len(articles) > 0, "No articles found for testing"
        
        # Generate story
        story = story_generator.generate_story(articles)
        
        # Count words (rough estimate of speaking time)
        word_count = len(story.split())
        assert 150 <= word_count <= 450, f"Story length ({word_count} words) outside acceptable range (150-450 words)"
        
        # Verify emotion markers
        emotion_markers = ["[SERIOUS]", "[EMPHASIS]", "[CULTURAL]", "[CALL_TO_ACTION]"]
        marker_count = sum(1 for marker in emotion_markers if marker in story)
        assert marker_count > 0, "Story should contain at least one emotion marker"
        
    except Exception as e:
        pytest.fail(f"Story length test failed: {str(e)}")
