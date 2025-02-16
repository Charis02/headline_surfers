from audio_generator import AudioGenerator
import os
from dotenv import load_dotenv

# Test story in Greek with Gen Z style
test_story = """Γεια σας φίλοι μου! Σήμερα έχουμε μια τέλεια είδηση να μοιραστούμε μαζί σας.
Ένας 19χρονος φοιτητής από την Αθήνα δημιούργησε μια εφαρμογή που σαρώνει! Σοβαρά, είναι φοβερό!
Η εφαρμογή βοηθάει τους μαθητές να οργανώνουν το διάβασμά τους με έναν super fun τρόπο, χαχα!
Ήδη την έχουν κατεβάσει πάνω από 10.000 άτομα... Τρελό, ε;
Για πείτε μου τώρα, δεν είναι τέλειο που η γενιά μας κάνει τέτοια πράγματα;"""

def main():
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # Get API key from environment variable
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        return

    # Create audio generator
    generator = AudioGenerator(api_key)
    
    # Generate audio
    success = generator.create_audio(test_story)
    
    if success:
        print("✨ Audio generation completed successfully!")
    else:
        print("❌ Audio generation failed.")

if __name__ == "__main__":
    main()