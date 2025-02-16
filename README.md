# Headline Surfers 🏄‍♂️📰

A Gen Z-style news aggregator that transforms Greek news articles into engaging TikTok content featuring AI-generated celebrity narrations.

## Features

- 🗞️ Fetches top 10 Greek news articles for any specified date
- 🤖 Uses LLM to rewrite news in Gen Z-friendly Greek language
- 🎭 Generates AI avatar videos of selected celebrities (Trump, Obama, Samuel L. Jackson)
- 🎮 Combines narration with Subway Surfers gameplay footage
- 🎥 Creates TikTok-ready video content

## Tech Stack

- Python 3.9+
- OpenAI GPT-4 for text generation
- D-ID/Elevenlabs for avatar generation
- NewsAPI for article fetching
- MoviePy for video editing
- TikTok API for posting

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/headline-surfers.git
cd headline-surfers
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

```bash
python src/main.py --date YYYY-MM-DD --celebrity "Barack Obama"
```

## Contributing

This is a hackathon project. Feel free to fork and improve! 