import requests
import json
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save

class AudioGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = ElevenLabs(api_key=self.api_key)
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

    def _format_news_text(self, text):
        """Format text with SSML adjustments based on standardized markers."""
        # First, clean up any incorrect closing tags for BREAK and LONG_BREAK
        text = text.replace('[/BREAK]', '')
        text = text.replace('[/LONG_BREAK]', '')
        
        # Replace markers with appropriate SSML tags
        replacements = {
            '[BREAK]': '<break time="500ms"/>',
            '[/BREAK]': '',
            '[LONG_BREAK]': '<break time="800ms"/>',
            '[/LONG_BREAK]': '',
            '[PITCH_HIGH]': '<prosody pitch="+30%" rate="120%">',
            '[/PITCH_HIGH]': '</prosody>',
            '[PITCH_MEDIUM]': '<prosody pitch="+20%">',
            '[/PITCH_MEDIUM]': '</prosody>',
            '[SLOW]': '<prosody rate="80%">',
            '[/SLOW]': '</prosody>',
            '[FAST]': '<prosody rate="120%">',
            '[/FAST]': '</prosody>',
            '[VOLUME_UP]': '<prosody volume="+4db">',
            '[/VOLUME_UP]': '</prosody>'
        }
        
        # Apply replacements
        formatted_text = text
        for marker, ssml in replacements.items():
            if '[/' not in marker:  # Only process opening tags here
                # Find all occurrences of the opening marker
                start_idx = 0
                while True:
                    start_idx = formatted_text.find(marker, start_idx)
                    if start_idx == -1:
                        break
                    # Find the next marker or end of the current phrase
                    next_marker_idx = float('inf')
                    for m in replacements.keys():
                        if '[/' not in m:  # Only look for opening markers
                            idx = formatted_text.find(m, start_idx + len(marker))
                            if idx != -1 and idx < next_marker_idx:
                                next_marker_idx = idx
                    
                    # If no next marker found, use end of sentence or paragraph
                    if next_marker_idx == float('inf'):
                        end_idx = formatted_text.find('.', start_idx)
                        if end_idx == -1:
                            end_idx = len(formatted_text)
                    else:
                        end_idx = next_marker_idx
                    
                    # Replace the marker and add closing tag
                    closing_marker = marker.replace('[', '[/')
                    formatted_text = formatted_text[:start_idx] + ssml + \
                                   formatted_text[start_idx + len(marker):end_idx] + \
                                   replacements[closing_marker] + \
                                   formatted_text[end_idx:]
                    start_idx += len(ssml)
        
        # Add basic sentence breaks
        formatted_text = formatted_text.replace(". ", ". <break time='300ms'/>")
        formatted_text = formatted_text.replace("! ", "! <break time='400ms'/>")
        formatted_text = formatted_text.replace("? ", "? <break time='400ms'/>")
        
        # Wrap in speak tags
        formatted_text = f"<speak>{formatted_text}</speak>"
        
        return formatted_text

    def create_audio(self, text, voice_id="n0vzWypeCK1NlWPVwhOc", output_file="test_news_audio.mp3"):
        """Generate audio using ElevenLabs TTS with specified voice."""
        try:
            # Format text with SSML tags
            formatted_text = self._format_news_text(text)
            
            # Make the API request
            audio_response = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=formatted_text
            )
            
            save(audio_response, output_file)
            
            return True
            
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return False 