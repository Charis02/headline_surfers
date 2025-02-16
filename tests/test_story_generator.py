import os
import sys
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.story_generator import StoryGenerator

# Sample Greek news articles for testing
SAMPLE_ARTICLES = [
    {
        "title": "Η Ελλάδα πρωτοπόρος στην πράσινη ενέργεια στην Ευρώπη",
        "content": """Η Ελλάδα σημειώνει σημαντική πρόοδο στον τομέα των ανανεώσιμων πηγών ενέργειας, 
        με τα φωτοβολταϊκά και αιολικά πάρκα να καλύπτουν πλέον το 40% των ενεργειακών αναγκών της χώρας. 
        Σύμφωνα με πρόσφατη έκθεση της Ευρωπαϊκής Επιτροπής, η Ελλάδα κατατάσσεται στις πρώτες θέσεις 
        στην ΕΕ όσον αφορά την αξιοποίηση της ηλιακής και αιολικής ενέργειας.""",
        "source": "Καθημερινή"
    },
    {
        "title": "Νέα επαναστατική ανακάλυψη Ελλήνων επιστημόνων στην τεχνητή νοημοσύνη",
        "content": """Ομάδα Ελλήνων ερευνητών από το Εθνικό Μετσόβιο Πολυτεχνείο ανέπτυξε έναν νέο 
        αλγόριθμο τεχνητής νοημοσύνης που μπορεί να προβλέψει με ακρίβεια 95% την εξέλιξη διαφόρων 
        ασθενειών. Η ανακάλυψη αυτή αναμένεται να φέρει επανάσταση στον τομέα της ιατρικής διάγνωσης.""",
        "source": "ΑΠΕ-ΜΠΕ"
    }
]

def test_story_generator_initialization():
    """Test that StoryGenerator initializes correctly"""
    generator = StoryGenerator()
    assert generator.api_key == os.getenv('GEMINI_API_KEY')
    assert "gemini-1.5-flash" in generator.base_url

def test_prepare_context():
    """Test that context is prepared correctly from articles"""
    generator = StoryGenerator()
    context = generator._prepare_context(SAMPLE_ARTICLES)
    
    # Check that all article titles are in the context
    for article in SAMPLE_ARTICLES:
        assert article['title'] in context
        assert article['source'] in context
        # Check that we're including the first 200 chars of content
        assert article['content'][:200] in context

@pytest.mark.integration
def test_generate_story():
    """Test that story generation works with the API
    Note: This is an integration test that requires a valid API key"""
    generator = StoryGenerator()
    story = generator.generate_story(SAMPLE_ARTICLES)
    
    # Basic validation of the generated story
    assert isinstance(story, str)
    assert len(story) > 0
    
    # Check that the story contains some Greek text
    # Looking for common Greek characters
    assert any(char in story for char in 'αβγδεζηθικλμνξοπρστυφχψω')
    
    # Check that it's not just returning the input
    assert story != SAMPLE_ARTICLES[0]['content']
    assert story != SAMPLE_ARTICLES[1]['content']

def test_generate_story_with_empty_articles():
    """Test that appropriate error is raised with empty articles"""
    generator = StoryGenerator()
    with pytest.raises(Exception) as exc_info:
        generator.generate_story([])
    assert "Error generating story" in str(exc_info.value)

def test_generate_story_with_invalid_api_key():
    """Test that appropriate error is raised with invalid API key"""
    generator = StoryGenerator()
    generator.api_key = "invalid_key"
    with pytest.raises(Exception) as exc_info:
        generator.generate_story(SAMPLE_ARTICLES)
    assert "Error generating story" in str(exc_info.value) 