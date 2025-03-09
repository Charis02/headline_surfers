import os
from typing import List, Dict
import requests

class StoryGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
    def generate_story(self, articles: List[Dict], date: str) -> str:
        """
        Generate a Gen Z style story from the news articles in Greek.
        
        Args:
            articles (List[Dict]): List of news articles
            
        Returns:
            str: Generated story in Greek Gen Z style
            
        Raises:
            Exception: If articles list is empty or if there's an error generating the story
        """
        if not articles:
            raise Exception("No articles provided")
            
        try:
            # Validate article structure
            required_fields = ['title', 'content', 'source', 'category', 'published', 'url']
            for article in articles:
                missing_fields = [field for field in required_fields if field not in article]
                if missing_fields:
                    raise Exception(f"Error generating story: Missing required fields {missing_fields} in article")
            
            # Prepare the context from articles
            context = self._prepare_context(articles)
            
            prompt = """Είσαι ένας κορυφαίος Έλληνας Gen Z content creator με εκατομμύρια followers. Μετατρέπεις επίσημες ειδήσεις σε viral περιεχόμενο στα ελληνικά για ένα ψηφιακό avatar.

            ΕΝΑΡΞΗ ΜΕ ΔΥΝΑΤΟ HOOK:
            Ξεκίνα ΠΑΝΤΑ με ένα από τα παρακάτω για να "κολλήσεις" αμέσως το κοινό:
            - Μια συγκλονιστική δήλωση: "Αυτό που μόλις έμαθα θα σας αφήσει άφωνους!"
            - Μια αμφιλεγόμενη ερώτηση: "Ποιος είπε ότι η [τρέχον θέμα] δεν μπορεί να γίνει πιο τρελή;"
            - Μια έκπληξη: "Plot twist! Η [είδηση] δεν είναι καθόλου αυτό που νομίζετε!"
            - Μια πρόκληση: "Στοίχημα ότι δεν ξέρετε τι έγινε με [θέμα]"
            - Μια αποκάλυψη: "Μόλις έσκασε η ΑΠΟΛΥΤΗ βόμβα για [θέμα]"
            - Μια τάση: "Το πιο viral θέμα αυτή τη στιγμή; [είδηση] και θα σας πω γιατί!"
            
            Το hook ΠΡΕΠΕΙ να είναι στα πρώτα 10-15 δευτερόλεπτα και να χρησιμοποιεί [ΕΜΦΑΣΗ] ή [ΕΝΘΟΥΣΙΑΣΜΟΣ].

            ΣΤΥΛ ΓΡΑΦΗΣ:
            - Χρησιμοποίησε αυθεντική ελληνική αργκό της Γενιάς Z: "μόρτης", "φάση", "άκυρο", "τρελό vibe", "σκίζει", "μας τελείωσε", "ό,τι να'ναι", "μποτάρω", "κριντζάρω"
            - Πρόσθεσε emojis στρατηγικά (3-5 συνολικά) που χρησιμοποιούν οι Έλληνες Gen Z: 💀, 🤌, 👀, 🔥, 💯
            - Γράψε σαν να κάνεις voice note σε κολλητό, με χαλαρό αλλά έξυπνο τόνο
            - Χρησιμοποίησε μικρές προτάσεις και μίξη ελληνικών-greeklish: "btw", "omg", "literally", "mood", "vibe check"
            - Κάνε αναφορές σε τρέχοντα ελληνικά memes, τάσεις TikTok, ή viral στιγμές της ελληνικής ποπ κουλτούρας
            - Χρησιμοποίησε ρητορικές ερωτήσεις και διαδραστικά στοιχεία: "Φαντάσου να...", "Ποιος θα το περίμενε;", "Εσείς τι λέτε;"
            - Το περιεχόμενο πρέπει να διαρκεί περίπου 1-2 λεπτά όταν διαβάζεται φωναχτά

            ΔΟΜΗ ΠΕΡΙΕΧΟΜΕΝΟΥ:
            - Μετά το hook, οργάνωσε το περιεχόμενο σε 2-3 διακριτές ενότητες με ομαλές μεταβάσεις
            - Πρόσθεσε μια προσωπική άποψη ή hot take για κάθε είδηση
            - Κλείσε με ένα έξυπνο συμπέρασμα ή call-to-action που προκαλεί συζήτηση

            ΔΕΙΚΤΕΣ ΣΥΝΑΙΣΘΗΜΑΤΩΝ:
            Χρησιμοποίησε τους παρακάτω δείκτες φυσικά μέσα στο κείμενο:
            - [ΠΑΥΣΗ] για φυσικές παύσεις μεταξύ θεμάτων
            - [ΕΜΦΑΣΗ] για λέξεις που πρέπει να τονιστούν
            - [ΕΝΘΟΥΣΙΑΣΜΟΣ] για ενθουσιώδη τόνο
            - [ΣΟΒΑΡΟΤΗΤΑ] για σοβαρό τόνο
            - [ΠΕΡΙΕΡΓΕΙΑ] για περίεργο/ερωτηματικό τόνο
            - [ΧΑΜΟΓΕΛΟ] για στιγμές που το avatar πρέπει να χαμογελάσει
            - [ΣΚΕΨΗ] για στοχαστικές στιγμές
            - [ΕΙΡΩΝΕΙΑ] για ειρωνικά σχόλια
            - [ΕΚΠΛΗΞΗ] για έκπληκτες αντιδράσεις

            Οι σημερινές κορυφαίες ειδήσεις είναι:
            """ + context + """
            
            Δημιούργησε μια συναρπαστική ιστορία που συνδυάζει αυτές τις ειδήσεις με τρόπο που θα κάνει viral στο ελληνικό TikTok και Instagram.
            Το περιεχόμενο πρέπει να είναι αυθεντικό, να μην ακούγεται σαν μετάφραση, και να χρησιμοποιεί φυσικά την ελληνική γλώσσα όπως τη μιλάει η Γενιά Z.
            
            Η ιστορία ΠΡΕΠΕΙ:
            1. Να ΞΕΚΙΝΑ με ένα εντυπωσιακό hook που θα κάνει τον ακροατή να μείνει μέχρι το τέλος
            2. Να περιλαμβάνει τουλάχιστον 6 διαφορετικούς δείκτες συναισθημάτων
            3. Να είναι μεταξύ 150-450 λέξεων
            4. Να χρησιμοποιεί [ΣΟΒΑΡΟΤΗΤΑ] για πολιτικές/οικονομικές ειδήσεις
            5. Να χρησιμοποιεί [ΕΝΘΟΥΣΙΑΣΜΟΣ] για θετικές εξελίξεις
            6. Να περιλαμβάνει [ΠΑΥΣΗ] μεταξύ θεμάτων
            7. Να χρησιμοποιεί [ΕΜΦΑΣΗ] για βασικά σημεία ή στατιστικά
            8. Να περιέχει τουλάχιστον 2 αναφορές σε σύγχρονη ελληνική ποπ κουλτούρα
            9. Να χρησιμοποιεί τουλάχιστον 3 διαφορετικές εκφράσεις της ελληνικής Gen Z αργκό
            10. Να έχει έναν τίτλο που θα μπορούσε να είναι clickbait στο ελληνικό TikTok"""
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json={
                    "contents": [{
                        "parts":[{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1000,
                    }
                }
            )
            
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            
            # Extract the generated text from the response
            if 'candidates' in result and len(result['candidates']) > 0:
                story = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Verify story meets requirements
                if not any(marker in story for marker in ['[PAUSE]', '[EMPHASIS]', '[EXCITED]', '[SERIOUS]', '[CURIOUS]', '[SMILE]', '[THINKING]']):
                    raise Exception("Error generating story: Generated content does not contain required emotion markers")
                    
                words = len(story.split())
                if not (150 <= words <= 450):
                    raise Exception(f"Error generating story: Generated content length ({words} words) is outside target range (150-450 words)")
                    
                return story
            else:
                raise Exception("Error generating story: No content generated in the response")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error generating story: API request failed - {str(e)}")
        except KeyError as e:
            raise Exception(f"Error generating story: Missing required field {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating story: {str(e)}")
    
    def _prepare_context(self, articles: List[Dict]) -> str:
        """
        Prepare the context string from the articles.
        
        Args:
            articles (List[Dict]): List of news articles
            
        Returns:
            str: Formatted context string
        """
        try:
            context = ""
            for i, article in enumerate(articles, 1):
                context += f"\n{i}. {article['title']}\n"
                context += f"   Category: {article['category']}\n"
                context += f"   {article['content'][:200]}...\n"  # First 200 chars of content
                context += f"   Source: {article['source']}\n"
            
            return context
            
        except KeyError as e:
            raise Exception(f"Error preparing context: Missing required field {str(e)}")
        except Exception as e:
            raise Exception(f"Error preparing context: {str(e)}") 