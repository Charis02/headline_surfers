import requests
import json
import os

class AudioGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

    def _format_news_text(self, text):
        """Format text with simple prosody adjustments for Gen Z style."""
        # Split text into sentences
        sentences = text.split('.')
        formatted_sentences = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # Base prosody for the sentence
            s = sentence.strip()
            
            # Add emphasis for exclamations
            if "!" in s:
                s = f"<prosody pitch='+30%' rate='120%'>{s}</prosody>"
            
            # Add curiosity for questions
            elif "?" in s:
                s = f"<prosody pitch='+20%' rate='90%'>{s}</prosody>"
            
            # Add emphasis for specific phrases
            s = s.replace("σοβαρά", "<prosody pitch='+20%' rate='90%'>σοβαρά</prosody>")
            s = s.replace("τέλειο", "<prosody pitch='+30%' rate='120%'>τέλειο</prosody>")
            s = s.replace("χαχα", "<prosody pitch='+20%' volume='+2db'>χαχα</prosody>")
            
            # Add pauses
            s = s.replace(",", ", <break time='300ms'/>")
            s = s.replace(";", "; <break time='500ms'/>")
            s = s.replace("...", "... <break time='800ms'/>")
            
            formatted_sentences.append(s)
        
        # Join sentences with appropriate breaks
        text = ". <break time='500ms'/>".join(formatted_sentences)
        
        # Wrap in speak tags
        text = f"<speak>{text}</speak>"
        
        return text

    def create_audio(self, text, output_file="test_news_audio.mp3"):
        """Generate audio using ElevenLabs TTS with Gen Z style."""
        try:
            # Format text with SSML tags
            formatted_text = self._format_news_text(text)
            print(f"Formatted text: {formatted_text[:100]}...")
            
            # Voice settings for a young, energetic voice
            voice_settings = {
                "stability": 0.71,
                "similarity_boost": 0.75,
                "style": 0.6,  # Increased style for more expressiveness
                "use_speaker_boost": True
            }
            
            # Request body
            data = {
                "text": formatted_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": voice_settings
            }
            
            # Make the API request
            # Using Antoni voice ID (better for multilingual content)
            voice_id = "ErXwobaYiN019PkySvjV"
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            print(f"Making request to: {url}")
            print(f"Headers: {json.dumps(self.headers, indent=2)}")
            print(f"Data: {json.dumps(data, indent=2)}")
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                # Save audio to file
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"Audio generated successfully and saved as {output_file}")
                return True
            else:
                print(f"Error: API request failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return False 