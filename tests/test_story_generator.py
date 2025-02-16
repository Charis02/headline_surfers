import os
import sys
import pytest
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.story_generator import StoryGenerator
from dotenv import load_dotenv

# Sample Greek news articles for testing
SAMPLE_ARTICLES = [
    {
        "title": "Η Ελλάδα πρωτοπόρος στην πράσινη ενέργεια στην Ευρώπη",
        "content": """Η Ελλάδα σημειώνει σημαντική πρόοδο στον τομέα των ανανεώσιμων πηγών ενέργειας, 
        με τα φωτοβολταϊκά και αιολικά πάρκα να καλύπτουν πλέον το 40% των ενεργειακών αναγκών της χώρας. 
        Σύμφωνα με πρόσφατη έκθεση της Ευρωπαϊκής Επιτροπής, η Ελλάδα κατατάσσεται στις πρώτες θέσεις 
        στην ΕΕ όσον αφορά την αξιοποίηση της ηλιακής και αιολικής ενέργειας.""",
        "source": "Καθημερινή",
        "category": "economy",
        "published": datetime.now().strftime('%Y-%m-%d'),
        "url": "https://www.kathimerini.gr/green-energy"
    },
    {
        "title": "Νέα επαναστατική ανακάλυψη Ελλήνων επιστημόνων στην τεχνητή νοημοσύνη",
        "content": """Ομάδα Ελλήνων ερευνητών από το Εθνικό Μετσόβιο Πολυτεχνείο ανέπτυξε έναν νέο 
        αλγόριθμο τεχνητής νοημοσύνης που μπορεί να προβλέψει με ακρίβεια 95% την εξέλιξη διαφόρων 
        ασθενειών. Η ανακάλυψη αυτή αναμένεται να φέρει επανάσταση στον τομέα της ιατρικής διάγνωσης.""",
        "source": "ΑΠΕ-ΜΠΕ",
        "category": "technology",
        "published": datetime.now().strftime('%Y-%m-%d'),
        "url": "https://www.amna.gr/tech-discovery"
    }
]

@pytest.fixture(autouse=True)
def debug_env():
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

@pytest.fixture
def story_generator():
    """Fixture to create a StoryGenerator instance for tests"""
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"Loaded API key (fixture): {api_key}")
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable not set")
    return StoryGenerator(api_key=api_key)

def test_story_generator_initialization(story_generator):
    """Test that StoryGenerator initializes correctly"""
    assert "gemini-1.5-flash" in story_generator.base_url

def test_prepare_context(story_generator):
    """Test that context is prepared correctly from articles"""
    context = story_generator._prepare_context(SAMPLE_ARTICLES)
    
    # Check that all article titles are in the context
    for article in SAMPLE_ARTICLES:
        assert article['title'] in context
        assert article['source'] in context
        assert article['category'] in context
        # Check that we're including the first 200 chars of content
        assert article['content'][:200] in context

@pytest.mark.integration
def test_generate_story(story_generator):
    """Test that story generation works with the API
    Note: This is an integration test that requires a valid API key"""
    story = story_generator.generate_story(SAMPLE_ARTICLES)
    
    # Basic validation of the generated story
    assert isinstance(story, str)
    assert len(story) > 0
    
    # Check for required emotion markers
    markers = ['[PAUSE]', '[EMPHASIS]', '[EXCITED]', '[SERIOUS]', 
              '[CURIOUS]', '[SMILE]', '[THINKING]']
    assert any(marker in story for marker in markers), "Story doesn't contain any emotion markers"
    
    # Check story length
    words = len(story.split())
    assert 150 <= words <= 450, f"Story length ({words} words) is outside target range"
    
    # Check for Greek text
    assert any(char in story for char in 'αβγδεζηθικλμνξοπρστυφχψω')
    
    # Check that it's not just returning the input
    assert story != SAMPLE_ARTICLES[0]['content']
    assert story != SAMPLE_ARTICLES[1]['content']

def test_generate_story_with_empty_articles(story_generator):
    """Test that appropriate error is raised with empty articles"""
    with pytest.raises(Exception) as exc_info:
        story_generator.generate_story([])
    assert "No articles provided" in str(exc_info.value)

def test_generate_story_with_missing_fields(story_generator):
    """Test that appropriate error is raised with missing fields"""
    invalid_article = {
        "title": "Test Article",
        "content": "Test content"
        # Missing required fields
    }
    with pytest.raises(Exception) as exc_info:
        story_generator.generate_story([invalid_article])
    assert "Missing required fields" in str(exc_info.value)

def test_generate_story_with_invalid_api_key():
    """Test that appropriate error is raised with invalid API key"""
    generator = StoryGenerator(api_key="invalid_key")
    with pytest.raises(Exception) as exc_info:
        generator.generate_story(SAMPLE_ARTICLES)
    assert "API request failed" in str(exc_info.value)

def test_story_requirements(story_generator):
    """Test that generated stories meet all requirements"""
    story = story_generator.generate_story(SAMPLE_ARTICLES)
    
    # Check for specific markers based on content type
    assert '[SERIOUS]' in story, "Economic news should have [SERIOUS] marker"
    assert '[EXCITED]' in story, "Technology discovery should have [EXCITED] marker"
    assert '[THINKING]' in story, "Statistics should have [THINKING] marker"
    assert '[PAUSE]' in story, "Story should have [PAUSE] between topics"
    
    # Check minimum number of markers
    markers = ['[PAUSE]', '[EMPHASIS]', '[EXCITED]', '[SERIOUS]', 
              '[CURIOUS]', '[SMILE]', '[THINKING]']
    marker_count = sum(1 for marker in markers if marker in story)
    assert marker_count >= 3, "Story should have at least 3 emotion markers" 