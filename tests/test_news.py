import os
import pytest
import sys
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from src.news_fetcher import NewsFetcher
from src.story_generator import StoryGenerator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def mock_gemini_response(mocker):
    """Fixture to mock Gemini API responses"""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        'candidates': [{
            'content': {
                'parts': [{
                    'text': '0,1,2'  # Mocked ranking response
                }]
            }
        }]
    }
    mock_response.raise_for_status = mocker.Mock()
    return mock_response

@pytest.fixture
def news_fetcher(mocker, mock_gemini_response):
    """Fixture to create a NewsFetcher instance with mocked API calls"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable not set")
    
    # Mock the requests.post call
    mocker.patch('requests.post', return_value=mock_gemini_response)
    
    return NewsFetcher(api_key=api_key)

@pytest.fixture
def story_generator():
    """Fixture to create a StoryGenerator instance"""
    return StoryGenerator(api_key=os.getenv('GEMINI_API_KEY'))

def test_news_fetcher_initialization_with_invalid_key():
    """Test that NewsFetcher raises error with invalid API key"""
    with pytest.raises(ValueError, match="API key cannot be empty"):
        NewsFetcher(api_key="")
    with pytest.raises(ValueError, match="API key cannot be empty"):
        NewsFetcher(api_key=None)

def test_news_fetcher_initialization(news_fetcher):
    """Test that NewsFetcher initializes correctly"""
    assert news_fetcher.max_articles == int(os.getenv('MAX_ARTICLES', 10))
    assert len(news_fetcher.sources) > 0
    assert all(source in news_fetcher.sources for source in ['cyprus_mail', 'in_cyprus', 'kathimerini_en'])

def test_fetch_articles(news_fetcher):
    """Test fetching articles for today's date"""
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        articles = news_fetcher.fetch_articles(today)
        
        assert isinstance(articles, list)
        if articles:  # If articles are found
            for article in articles:
                assert isinstance(article, dict)
                required_keys = {'title', 'content', 'url', 'source', 'category', 'published'}
                assert all(key in article for key in required_keys), f"Missing required key in article: {required_keys - set(article.keys())}"
                assert all(isinstance(article[key], str) for key in required_keys), "All article values should be strings"
    except requests.exceptions.RequestException as e:
        pytest.skip(f"API request failed: {str(e)}")
    except Exception as e:
        if "No articles found" in str(e):
            pytest.skip("No articles available for testing")
        raise

def test_article_categories(news_fetcher):
    """Test that articles are properly categorized"""
    today = datetime.now().strftime('%Y-%m-%d')
    articles = news_fetcher.fetch_articles(today)
    
    if articles:
        valid_categories = {'politics', 'economy', 'society', 'world', 'sports', 'general'}
        for article in articles:
            assert article['category'] in valid_categories, f"Invalid category: {article['category']}"

def test_article_date_filtering(news_fetcher):
    """Test that articles are properly filtered by date"""
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    today_articles = news_fetcher.fetch_articles(today)
    assert len(today_articles) > 0, "Should find articles for today"
    
    # For past dates, it's okay to have no articles
    try:
        yesterday_articles = news_fetcher.fetch_articles(yesterday)
        if yesterday_articles:
            today_urls = {article['url'] for article in today_articles}
            yesterday_urls = {article['url'] for article in yesterday_articles}
            assert today_urls != yesterday_urls, "Same articles returned for different dates"
    except Exception as e:
        assert "No articles found" in str(e), "Unexpected error for past date"

def test_article_source_validation(news_fetcher):
    """Test that articles come from valid sources"""
    today = datetime.now().strftime('%Y-%m-%d')
    articles = news_fetcher.fetch_articles(today)
    
    valid_sources = set(news_fetcher.sources.keys())
    if articles:
        for article in articles:
            assert article['source'] in valid_sources, f"Invalid source: {article['source']}"

def test_article_content_length(news_fetcher):
    """Test that article content meets minimum length requirements"""
    today = datetime.now().strftime('%Y-%m-%d')
    articles = news_fetcher.fetch_articles(today)
    
    if articles:
        for article in articles:
            assert len(article['content']) >= 100, "Article content too short"
            assert len(article['title']) >= 10, "Article title too short"

def test_error_handling(news_fetcher):
    """Test error handling for invalid inputs"""
    # Test invalid date format
    with pytest.raises(Exception) as exc_info:
        news_fetcher.fetch_articles("invalid-date")
    assert "Error fetching news articles" in str(exc_info.value)
    
    # Test future date
    future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    with pytest.raises(Exception) as exc_info:
        news_fetcher.fetch_articles(future_date)
    assert "No articles found" in str(exc_info.value)

@pytest.mark.integration
def test_complete_pipeline(news_fetcher, story_generator, mocker):
    """Test the complete news fetching and story generation pipeline"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Mock the RSS feed response
    test_articles = [
        {
            'title': 'Major political reform in Cyprus',
            'content': 'Significant changes to government structure',
            'category': 'politics',
            'source': 'cyprus_mail',
            'url': 'http://example.com/1',
            'published': today
        },
        {
            'title': 'Local festival celebrates culture',
            'content': 'Annual cultural event draws crowds',
            'category': 'society',
            'source': 'in_cyprus',
            'url': 'http://example.com/2',
            'published': today
        }
    ]
    
    # Mock the _fetch_from_rss method
    mocker.patch.object(
        news_fetcher, 
        '_fetch_from_rss', 
        return_value=test_articles
    )
    
    # Mock story generator response
    mock_story_response = mocker.Mock()
    mock_story_response.json.return_value = {
        'candidates': [{
            'content': {
                'parts': [{
                    'text': """[SERIOUS] Σημαντικές εξελίξεις στην Κύπρο σήμερα, φίλοι μου! 🔥 Η κυβέρνηση ανακοίνωσε μεγάλες αλλαγές στη δομή των θεσμών [EMPHASIS] που θα επηρεάσουν τη ζωή όλων μας. Πρόκειται για μια ιστορική στιγμή που θα καθορίσει το μέλλον της χώρας μας.

[THINKING] Οι μεταρρυθμίσεις αυτές στοχεύουν στον εκσυγχρονισμό της δημόσιας διοίκησης και την καλύτερη εξυπηρέτηση των πολιτών. [PAUSE] Αναμένεται να δούμε σημαντικές βελτιώσεις στην καθημερινότητά μας. Σύμφωνα με τους ειδικούς, οι αλλαγές θα επιφέρουν μείωση της γραφειοκρατίας κατά 40% και θα επιταχύνουν τις διαδικασίες εξυπηρέτησης των πολιτών.

[EXCITED] Και τώρα, κάτι πιο ευχάριστο! 🎉 [SMILE] Οι τοπικές κοινότητες ενώνονται για να γιορτάσουν την πλούσια πολιτιστική μας κληρονομιά. Φεστιβάλ, μουσική, χοροί και παραδοσιακές γεύσεις - όλα σε ένα απίθανο event! Περισσότεροι από 1000 καλλιτέχνες και 50 κοινότητες θα συμμετάσχουν σε αυτή τη μοναδική γιορτή πολιτισμού.

[THINKING] Η σημασία αυτών των εκδηλώσεων είναι τεράστια για τη διατήρηση της πολιτιστικής μας ταυτότητας. [PAUSE] Είναι μια ευκαιρία να δείξουμε στη νέα γενιά την ομορφιά των παραδόσεών μας με έναν σύγχρονο και διασκεδαστικό τρόπο.

[CURIOUS] Πώς βλέπετε εσείς αυτές τις εξελίξεις; Πιστεύετε ότι οι αλλαγές θα φέρουν το επιθυμητό αποτέλεσμα; [PAUSE] Πείτε μας τη γνώμη σας στα σχόλια! 👇

[EMPHASIS] Μείνετε συντονισμένοι για περισσότερες ειδήσεις και updates! 🎯 Θα επανέλθουμε με περισσότερες λεπτομέρειες για τις εκδηλώσεις και την πορεία των μεταρρυθμίσεων."""
                }]
            }
        }]
    }
    
    # Replace the requests.post for story generation
    original_post = requests.post
    def mock_post(url, **kwargs):
        if 'story' in kwargs.get('json', {}).get('contents', [{}])[0].get('parts', [{}])[0].get('text', '').lower():
            return mock_story_response
        return original_post(url, **kwargs)
    
    mocker.patch('requests.post', side_effect=mock_post)
    
    try:
        # Fetch articles
        articles = news_fetcher.fetch_articles(today)
        assert isinstance(articles, list)
        assert len(articles) > 0, "Should have test articles"
        
        # Generate story from up to 3 articles
        test_articles = articles[:min(3, len(articles))]
        story = story_generator.generate_story(test_articles)
        
        assert isinstance(story, str)
        assert len(story) > 0
        
        # Verify story requirements with more flexible bounds
        words = len(story.split())
        assert 100 <= words <= 500, f"Story length ({words} words) is outside acceptable range"
        
        # Verify at least one emotion marker is present
        markers = ['[PAUSE]', '[EMPHASIS]', '[EXCITED]', '[SERIOUS]', 
                  '[CURIOUS]', '[SMILE]', '[THINKING]']
        assert any(marker in story for marker in markers), "Story doesn't contain any emotion markers"
        
    except requests.exceptions.RequestException as e:
        pytest.skip(f"API request failed: {str(e)}")
    except Exception as e:
        if "No articles found" in str(e):
            pytest.skip("No articles available for testing")
        raise

def test_category_detection(news_fetcher):
    """Test article category detection"""
    test_cases = [
        {
            'title': 'Cyprus Parliament passes new economic bill',
            'description': 'The government announced new financial measures',
            'expected': 'politics'
        },
        {
            'title': 'Market update: Euro strengthens against dollar',
            'description': 'Financial markets show positive trends',
            'expected': 'economy'
        },
        {
            'title': 'Local school implements new education program',
            'description': 'Students benefit from innovative teaching methods',
            'expected': 'society'
        }
    ]
    
    for case in test_cases:
        category = news_fetcher._detect_category(case['title'], case['description'])
        assert category == case['expected']

def test_date_parsing(news_fetcher):
    """Test parsing of different date formats"""
    test_dates = [
        '2024-02-15T14:30:00+0200',
        'Fri, 15 Feb 2024 14:30:00 +0000',
        '2024-02-15 14:30:00',
        'Fri, 15 Feb 2024 14:30:00 GMT',
        '2024-02-15T14:30:00Z'
    ]
    
    for date_str in test_dates:
        parsed_date = news_fetcher._parse_date(date_str)
        assert isinstance(parsed_date, datetime)

def test_rss_fetching(news_fetcher):
    """Test fetching articles from RSS feeds"""
    today = datetime.now().date()
    articles = news_fetcher._fetch_from_rss(today)
    
    assert isinstance(articles, list)
    if articles:
        for article in articles:
            assert all(key in article for key in ['title', 'content', 'url', 'source', 'category', 'published'])
            assert article['source'] in news_fetcher.sources

@pytest.mark.unit
def test_article_ranking(news_fetcher, mocker):
    """Test article ranking functionality with mocked API response"""
    # Mock the requests.post response
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        'candidates': [{
            'content': {
                'parts': [{
                    'text': '0,1'  # Mocked ranking response
                }]
            }
        }]
    }
    mock_response.raise_for_status = mocker.Mock()
    
    mocker.patch('requests.post', return_value=mock_response)
    
    test_articles = [
        {
            'title': 'Major political reform in Cyprus',
            'content': 'Significant changes to government structure',
            'category': 'politics',
            'source': 'cyprus_mail',
            'url': 'http://example.com/1',
            'published': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'title': 'Local festival celebrates culture',
            'content': 'Annual cultural event draws crowds',
            'category': 'society',
            'source': 'in_cyprus',
            'url': 'http://example.com/2',
            'published': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    
    ranked_articles = news_fetcher._rank_articles(test_articles)
    assert isinstance(ranked_articles, list)
    assert len(ranked_articles) == len(test_articles)
    assert ranked_articles[0]['title'] == test_articles[0]['title']  # Verify ranking order 