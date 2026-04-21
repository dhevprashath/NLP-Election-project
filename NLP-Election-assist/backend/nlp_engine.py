import re
import os
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
from data import PARTIES as FULL_PARTY_DATABASE, NATIONAL_STATISTICS

ELECTION_KEYWORDS = [
    "party", "parties", "slogan", "symbol", "cm", "minister", "vote", "election", 
    "candidate", "poll", "dmk", "aiadmk", "bjp", "ntk", "congress", "tvk", "tvke", "inc", "pmk", "dmdk", "mdmk", "vck", "cpi", "cpim", "communist", "comunist",
    "stalin", "edappadi", "annamalai", "seeman", "vijay", "leader", "captain", "vijayakanth", "anbumani", "thirumavalavan", "vaiko",
    "mla", "mp", "politics", "manifesto", "dravidam", "amma", "alliance", "founder", "founded", "tamilaga", "tamizhaga",
    "song", "songs", "anthem", "youtube", "music", "video", "rajya sabha", "leadership", "president", "secretary", "ideology", "flag", "hammer", "sickle", "logo", "tamil nadu", "tn", "list", "show",
    "india", "national", "country", "election commission", "eci"
]

class NLPEngine:
    def __init__(self):
        self.parties = FULL_PARTY_DATABASE
        self.keywords = ELECTION_KEYWORDS
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'intent_model.joblib')
        self._load_model()

    def _load_model(self):
        if not HAS_JOBLIB:
            print("Joblib not installed. ML model disabled.")
            return
            
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"NLP Model loaded from {self.model_path}")
            else:
                print(f"Warning: NLP Model not found at {self.model_path}. Falling back to rule-based classification.")
        except Exception as e:
            print(f"Error loading NLP Model: {e}. Falling back to rule-based classification.")

    def _is_person_in_text(self, person_name: str, text: str) -> bool:
        if not person_name: return False
        clean_name = re.sub(r'[^\w\s]', '', person_name.lower())
        # Ignore initials and short words
        parts = [p for p in clean_name.split() if len(p) > 2]
        for part in parts:
            if re.search(r'\b' + re.escape(part) + r'\b', text):
                return True
        return False

    def is_domain_relevant(self, text: str) -> bool:
        """
        Simple keyword matching to check if the query is likely about elections.
        Also returns True if any party name or leader or slogan is found.
        """
        # Strip punctuation for cleaner matching
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Check basic election keywords
        for keyword in self.keywords:
            if keyword in text:
                return True
        
        # Check specific party data
        for party_key, data in self.parties.items():
            clean_key = re.sub(r'[^\w\s]', '', party_key.lower())
            clean_name = re.sub(r'[^\w\s]', '', data['name'].lower())
            party_match = (
                f" {clean_key} " in f" {text} " or 
                f" {clean_name} " in f" {text} " or 
                data['full_name'].lower() in text
            )
            if party_match:
                return True
            if self._is_person_in_text(data.get("cm_candidate_tn", ""), text):
                return True
            if "founder" in data and self._is_person_in_text(data["founder"], text):
                return True
            for slogan in data["slogans"]:
                if slogan.lower() in text:
                    return True
            
            # Check leadership
            for person in data["leadership"].values():
                if self._is_person_in_text(person, text):
                    return True
            
            # Check roles
            for role_data in data.get("important_roles_in_party", []):
                if self._is_person_in_text(role_data.get("name", ""), text):
                    return True
                    
        return False

    def classify_intent(self, text: str):
        """
        Classifies the intent of the user query.
        Returns a tuple: (intent_type, relevant_data)
        """
        # Clean text for robust matching
        orig_text = text.lower()
        text = re.sub(r'[^\w\s]', '', orig_text)
        
        if not self.is_domain_relevant(orig_text):
            return "OUT_OF_DOMAIN", None

        # Determine the party/entity first
        detected_party = None
        # Sort keys by length descending to match "CPI(M)" before "CPI"
        sorted_keys = sorted(self.parties.keys(), key=len, reverse=True)
        
        for party_key in sorted_keys:
            data = self.parties[party_key]
            clean_key = re.sub(r'[^\w\s]', '', party_key.lower())
            clean_name = re.sub(r'[^\w\s]', '', data['name'].lower())
            
            # Match party key, name, or full name
            if (f" {clean_key} " in f" {text} " or 
                f" {clean_name} " in f" {text} " or 
                data['full_name'].lower() in text or
                (party_key == "INC" and "congress" in text) or
                (party_key == "TVK" and ("tvke" in text or "tv ke" in text)) or
                (party_key in ["CPI", "CPI(M)"] and ("communist" in text or "comunist" in text))): # Specific case for Communist parties
                detected_party = party_key
                break
        
        if not detected_party:
            # Search specifically for leaders or candidates
            for party_key in sorted_keys:
                data = self.parties[party_key]
                if self._is_person_in_text(data.get("cm_candidate_tn", ""), text):
                    detected_party = party_key
                    break
                for person in data["leadership"].values():
                    if self._is_person_in_text(person, text):
                        detected_party = party_key
                        break
                if detected_party: break
                for role_data in data.get("important_roles_in_party", []):
                    if self._is_person_in_text(role_data.get("name", ""), text):
                        detected_party = party_key
                        break
                if detected_party: break

        # 1. HIGH-CONFIDENCE RULE MATCHING (Check before ML)
        # Helper for word boundary check
        def has_word(t, word):
            return re.search(r'\b' + re.escape(word) + r'\b', t)

        # List/Count Parties Query
        if any(kw in text for kw in ["how many", "what are", "who are", "which are", "list", "show all"]) and any(p_kw in text for p_kw in ["parties", "party"]):
            if any(i_kw in text for i_kw in ["india", "national", "country", "bharat"]):
                return "LIST_PARTIES_QUERY", "INDIA"
            return "LIST_PARTIES_QUERY", "ALL"
        
        # Another pattern: "parties in tamil nadu" or "parties in tn"
        if ("parties" in text or "party" in text) and ("tamil nadu" in text or "tn " in text or " tn" in text):
             return "LIST_PARTIES_QUERY", "ALL"
        
        # Specific India pattern
        if ("parties" in text or "party" in text) and any(i_kw in text for i_kw in ["india", "national", "country", "bharat"]):
             return "LIST_PARTIES_QUERY", "INDIA"

        # 0. PRIORITIZE HISTORY/RULING YEARS (Most problematic recently)
        if any(kw in text for kw in ["history", "rule", "years", "government", "government", "governments", "ruling"]):
            if detected_party: 
                return "HISTORY_QUERY", detected_party

        # Check for Slogans
        for party_key, data in self.parties.items():
            for slogan in data["slogans"]:
                if slogan.lower() in text:
                    return "SLOGAN_DETECTED", party_key

        # Song Query
        if any(kw in text for kw in ["song", "anthem", "music", "video", "youtube"]):
             if detected_party: return "SONG_QUERY", detected_party

        # Flag Query
        if has_word(text, "flag") or "kodi" in text:
            if detected_party: return "FLAG_QUERY", detected_party

        # MLA Query
        if has_word(text, "mla") or has_word(text, "mlas") or "members of legislative assembly" in text:
            if detected_party: return "MLA_QUERY", detected_party

        # MP Query
        if has_word(text, "mp") or has_word(text, "mps") or "member of parliament" in text or "lok sabha" in text:
            if detected_party: return "MP_QUERY", detected_party

        # Rajya Sabha Query
        if "rajya sabha" in text:
            if detected_party: return "RAJYA_SABHA_QUERY", detected_party

        # Ideology Query
        if "ideology" in text or "principles" in text or "policy" in text:
            if detected_party: return "IDEOLOGY_QUERY", detected_party

        # Slogan Query
        if "slogan" in text or "motto" in text:
             if detected_party: return "SLOGAN_QUERY", detected_party

        # Symbol Query
        if "symbol" in text or "logo" in text:
             if detected_party: return "SYMBOL_QUERY", detected_party

        # Constituency Query
        if "constituency" in text or " தொகுதி " in text:
             if detected_party: return "CONSTITUENCY_QUERY", detected_party

        # 3. OTHER RULE MATCHING (Fallback/Secondary)
        # Founder Query
        if "founder" in text or "founded" in text or "started by" in text:
             if detected_party: return "FOUNDER_QUERY", detected_party

        # Alliance Query
        if "alliance" in text or "partner" in text or "coalition" in text:
             if detected_party: return "ALLIANCE_QUERY", detected_party
        
        # Leadership / Secretary / President Query
        if "president" in text or "secretary" in text or "leader" in text or "leadership" in text or "roles" in text:
            if detected_party: return "LEADERSHIP_QUERY", detected_party

        # Proposed CM Query
        if has_word(text, "cm") or "minister" in text or "candidate" in text:
            if detected_party: return "PROPOSED_CM_QUERY", detected_party

        # 4. Specific Leader fallback
        # If the user specifically entered a leader's name and no other intent was found
        if detected_party:
            data = self.parties[detected_party]
            if self._is_person_in_text(data.get("cm_candidate_tn", ""), text):
                return "LEADERSHIP_QUERY", detected_party
            for person in data["leadership"].values():
                if self._is_person_in_text(person, text):
                    return "LEADERSHIP_QUERY", detected_party
            for role_data in data.get("important_roles_in_party", []):
                if self._is_person_in_text(role_data.get("name", ""), text):
                    return "LEADERSHIP_QUERY", detected_party
            
            # General Party Info fallback
            return "PARTY_INFO", detected_party

        return "UNKNOWN_ELECTION_QUERY", None

    def get_response(self, text: str):
        intent, data_key = self.classify_intent(text)
        
        if intent == "OUT_OF_DOMAIN":
            return {
                "response_text": "Sorry, I am not trained for this domain.",
                "intent": intent
            }

        if intent == "LIST_PARTIES_QUERY":
            if data_key == "INDIA":
                stats = NATIONAL_STATISTICS
                resp = f"According to the Election Commission of India ({stats['last_updated']}):\n\n"
                resp += f"- Total Registered Parties: {stats['total_registered_parties']}\n"
                resp += f"- National Parties: {stats['national_parties_count']} ({', '.join(stats['national_parties_list'])})\n"
                resp += f"- State Parties: {stats['state_parties_count']}\n"
                resp += "\nIndia has a multi-party system with a large number of regional and national players."
                return {
                    "response_text": resp,
                    "intent": intent,
                    "data": stats
                }
            
            party_names = [f"{data['full_name']} ({key})" for key, data in self.parties.items()]
            return {
                "response_text": f"I currently have information on {len(self.parties)} parties in Tamil Nadu:\n" + "\n".join([f"- {name}" for name in party_names]),
                "intent": intent,
                "data": {"count": len(self.parties), "parties": list(self.parties.keys())}
            }
            
        if not data_key:
             return {
                "response_text": "I understood this is about the election, but I couldn't identify the specific party or question. Try asking about a party slogan, MLA, MP, leadership, or CM candidate.",
                "intent": intent
            }

        party = self.parties[data_key]
        clean_text = re.sub(r'[^\w\s]', '', text.lower())

        if intent == "CONSTITUENCY_QUERY":
            # Check for CM/Leader constituency
            if "cm" in clean_text or party["cm_candidate_tn"].lower() in clean_text:
                constituency = party.get("cm_mla_constituency", "Unknown")
                return {
                    "response_text": f"The current CM candidate/leader for {party['name']}, {party['cm_candidate_tn']}, represents the {constituency} constituency.",
                    "intent": intent,
                    "data": party
                }
            
            # Check specific MLAs in sample
            for mla in party.get("mlas_tn_sample", []):
                if mla["name"].lower() in clean_text:
                    return {
                        "response_text": f"{mla['name']} is the MLA for {mla['constituency']} representing {party['name']}.",
                        "intent": intent,
                        "data": party
                    }
                if mla["constituency"].lower() in clean_text:
                    return {
                        "response_text": f"The MLA for {mla['constituency']} is {mla['name']} from {party['name']}.",
                        "intent": intent,
                        "data": party
                    }
                    
            return {
                "response_text": f"I have some sample MLA data for {party['name']}. You can ask about leaders like {party['cm_candidate_tn']} or prominent MLAs.",
                "intent": intent,
                "data": party
            }

        if intent == "SLOGAN_DETECTED":
            slogans_list = "\n".join([f"- {s}" for s in party['slogans']])
            return {
                "response_text": f"Slogan Detected! This belongs to {party['name']}.\n\nOfficial Slogans:\n{slogans_list}",
                "intent": intent,
                "data": party
            }
        
        if intent == "SLOGAN_QUERY":
            slogans_list = "\n".join([f"- {s}" for s in party['slogans']])
            return {
                "response_text": f"The slogans for {party['name']} are:\n{slogans_list}",
                "intent": intent,
                "data": party
            }
        
        if intent == "FOUNDER_QUERY":
            founder_text = f"The founder of {party['name']} is {party.get('founder', 'Unknown')}."
            if "founded_year" in party:
                founder_text += f"\nFounded in: {party['founded_year']}"
            return {
                "response_text": founder_text,
                "intent": intent,
                "data": party
            }

        if intent == "ALLIANCE_QUERY":
            return {
                "response_text": f"{party['name']} is part of: {party.get('alliances', 'Unknown Alliances')}.",
                "intent": intent,
                "data": party
            }
            
        if intent == "HISTORY_QUERY":
            history_text = f"{party['name']} Ruling History in Tamil Nadu:\n"
            history = party.get("chief_minister_history_tn", [])
            if history:
                for term in history:
                    history_text += f"- {term['name']} ({term['term_from']} - {term['term_to']})\n"
            else:
                history_text += "No records of this party ruling Tamil Nadu as a major power."
            return {
                "response_text": history_text,
                "intent": intent,
                "data": party
            }

        if intent == "PROPOSED_CM_QUERY":
            return {
                "response_text": f"The proposed CM candidate for {party['name']} is {party['cm_candidate_tn']}.",
                "intent": intent,
                "data": party
            }
            
        if intent == "LEADERSHIP_QUERY":
            leadership = party['leadership']
            roles = party.get('important_roles_in_party', [])
            resp = f"Leadership of {party['name']}:\n"
            resp += f"- National President: {leadership['national_president']}\n"
            resp += f"- State President (TN): {leadership['state_president_tn']}\n"
            resp += f"- General Secretary: {leadership['general_secretary']}\n"
            if roles:
                resp += "\nImportant Roles:\n"
                for r in roles:
                    resp += f"- {r['role']}: {r['name']}\n"
            return {
                "response_text": resp,
                "intent": intent,
                "data": party
            }

        if intent == "MLA_QUERY":
            mlas = party.get("mlas_tn_sample", [])
            if mlas:
                resp = f"Sample MLAs of {party['name']} in Tamil Nadu:\n"
                for mla in mlas:
                    resp += f"- {mla['name']} ({mla['constituency']})\n"
                return {
                    "response_text": resp,
                    "intent": intent,
                    "data": party
                }
            return {"response_text": f"No sample MLAs listed for {party['name']}.", "intent": intent, "data": party}

        if intent == "MP_QUERY":
            mps = party.get("mps_lok_sabha_sample", [])
            if mps:
                resp = f"Sample Lok Sabha MPs of {party['name']} from Tamil Nadu:\n"
                for mp in mps:
                    resp += f"- {mp['name']} ({mp['constituency']})\n"
                return {
                    "response_text": resp,
                    "intent": intent,
                    "data": party
                }
            return {"response_text": f"No sample Lok Sabha MPs listed for {party['name']}.", "intent": intent, "data": party}

        if intent == "RAJYA_SABHA_QUERY":
            rs = party.get("rajya_sabha_members_sample", [])
            if rs:
                resp = f"Sample Rajya Sabha members of {party['name']}:\n"
                for member in rs:
                    resp += f"- {member['name']}\n"
                return {
                    "response_text": resp,
                    "intent": intent,
                    "data": party
                }
            return {"response_text": f"No sample Rajya Sabha members listed for {party['name']}.", "intent": intent, "data": party}

        if intent == "IDEOLOGY_QUERY":
            return {
                "response_text": f"The ideology of {party['name']} is: {party['party_ideology']}.",
                "intent": intent,
                "data": party
            }

        if intent == "FLAG_QUERY":
            # For flags, prioritize flag_url
            flag_url = party.get('flag_url') or party.get('image_url')
            return {
                "response_text": f"The flag of {party['name']} is: {party.get('flag_description', 'No specific description available.')}",
                "intent": intent,
                "data": {**party, "image_url": flag_url} if flag_url else party
            }

        if intent == "SONG_QUERY":
            songs = party.get("songs", [])
            if songs:
                song_text = f"Official songs/anthems for {party['name']}:\n"
                for s in songs:
                    song_text += f"- {s['title']}: {s['url']}\n"
                return {
                    "response_text": song_text,
                    "intent": intent,
                    "data": party
                }
            return {
                "response_text": f"You can search for {party['name']} election songs on YouTube. Key slogans include: {', '.join(party['slogans'][:2])}.",
                "intent": intent,
                "data": party
            }
            
        if intent == "SYMBOL_QUERY":
            # For symbols/logos, use image_url
            logo_url = party.get('image_url') or party.get('flag_url')
            return {
                "response_text": f"The symbol for {party['name']} ({party['full_name']}) is recognized in the Election Commission records. You can ask about their slogans or leaders for more details.",
                "intent": intent,
                "data": {**party, "image_url": logo_url} if logo_url else party
            }
            
        if intent == "PARTY_INFO":
            info = f"{party['name']} ({party['full_name']})\n"
            info += f"Ideology: {party['party_ideology']}\n"
            info += f"Leader/CM Candidate: {party['cm_candidate_tn']}\n"
            info += f"Founder: {party['founder']} ({party['founded_year']})\n"
            info += f"Alliance: {party['alliances']}\n"
            slogans_str = ", ".join(party['slogans'])
            info += f"Slogans: {slogans_str}"
            return {
                "response_text": info,
                "intent": intent,
                "data": party
            }

        return {
            "response_text": "I understood this is about the election, but I couldn't identify the specific question. Try asking about a party slogan, MLA, MP, leadership, or CM candidate.",
            "intent": intent
        }

    def get_suggestions(self, query: str):
        query = query.lower()
        suggestions = []
        
        # Suggest Party Names
        for party in self.parties.keys():
            if query in party.lower():
                suggestions.append(party)
        
        # Suggest CM Candidates
        for party in self.parties.values():
            if query in party["cm_candidate_tn"].lower():
                suggestions.append(party["cm_candidate_tn"])
                 
        return list(set(suggestions))[:5] # Return top 5 unique suggestions
