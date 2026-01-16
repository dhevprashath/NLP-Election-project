import re
from data import PARTIES, ELECTION_KEYWORDS

class NLPEngine:
    def __init__(self):
        self.parties = PARTIES
        self.keywords = ELECTION_KEYWORDS

    def is_domain_relevant(self, text: str) -> bool:
        """
        Simple keyword matching to check if the query is likely about elections.
        Also returns True if any party name or leader or slogan is found.
        """
        text = text.lower()
        
        # Check basic election keywords
        for keyword in self.keywords:
            if keyword in text:
                return True
        
        # Check specific party data
        for party_key, data in self.parties.items():
            if party_key.lower() in text or data["name"].lower() in text:
                return True
            if data["symbol"].lower() in text:
                return True
            if data["proposed_cm"].lower() in text:
                return True
            if "founder" in data and data["founder"].lower() in text:
                return True
            for slogan in data["slogans"]:
                if slogan in text:
                    return True
            for leader in data["leaders"]:
                if leader.lower() in text:
                    return True
                    
        return False

    def classify_intent(self, text: str):
        """
        Classifies the intent of the user query.
        Returns a tuple: (intent_type, relevant_data)
        """
        text = text.lower()
        
        if not self.is_domain_relevant(text):
            return "OUT_OF_DOMAIN", None

        # 1. Check for Slogans (Exact or partial substring match)
        for party_key, data in self.parties.items():
            for slogan in data["slogans"]:
                if slogan in text:
                    return "SLOGAN_DETECTED", party_key

        # 2. Founder Query
        if "founder" in text or "founded" in text or "started by" in text:
             for party_key, data in self.parties.items():
                if party_key.lower() in text:
                    return "FOUNDER_QUERY", party_key

        # 3. Alliance Query
        if "alliance" in text or "partner" in text or "coalition" in text:
             for party_key, data in self.parties.items():
                if party_key.lower() in text:
                    return "ALLIANCE_QUERY", party_key
        
        # 4. History / Ruling Years Query
        if "history" in text or "rule" in text or "years" in text or "government" in text:
             for party_key, data in self.parties.items():
                if party_key.lower() in text:
                    return "HISTORY_QUERY", party_key

        # 5. Check for "Who is CM" or "Proposed CM" or "Candidate"
        if "cm" in text or "minister" in text or "candidate" in text or "leader" in text:
            # Determine which party
            for party_key, data in self.parties.items():
                if party_key.lower() in text or data["full_name"].lower() in text:
                    return "PROPOSED_CM_QUERY", party_key
            
            # If asking generally about a person (e.g. "Who is Stalin?")
            for party_key, data in self.parties.items():
                 # Check proposed_cm
                 if data["proposed_cm"].lower() in text:
                     return "LEADER_INFO", party_key
                 # Check other leaders
                 if "leaders" in data:
                     for leader in data["leaders"]:
                         if leader.lower() in text:
                             return "LEADER_INFO", party_key

        # 6. Check for Symbol identification
        if "symbol" in text:
            # "What is symbol of DMK?"
            for party_key, data in self.parties.items():
                if party_key.lower() in text:
                    return "SYMBOL_QUERY", party_key
            
            # "Which party has Two Leaves?"
            for party_key, data in self.parties.items():
                if data["symbol"].lower() in text:
                    return "SYMBOL_IDENTIFICATION", party_key

        # 7. General Party Info
        for party_key, data in self.parties.items():
            if party_key.lower() in text:
                return "PARTY_INFO", party_key

        return "UNKNOWN_ELECTION_QUERY", None

    def get_response(self, text: str):
        intent, data_key = self.classify_intent(text)
        
        if intent == "OUT_OF_DOMAIN":
            return {
                "response_text": "Sorry, I am not trained for this domain.",
                "intent": intent
            }
            
        if intent == "SLOGAN_DETECTED":
            party = self.parties[data_key]
            return {
                "response_text": f"Party Name: {party['name']}\nSymbol: {party['symbol']}",
                "intent": intent,
                "data": party
            }
        
        if intent == "FOUNDER_QUERY":
            party = self.parties[data_key]
            founder_text = f"The founder of {party['name']} is {party.get('founder', 'Unknown')}."
            if "founded_year" in party:
                founder_text += f"\nFounded in: {party['founded_year']}"
            return {
                "response_text": founder_text,
                "intent": intent,
                "data": party
            }

        if intent == "ALLIANCE_QUERY":
            party = self.parties[data_key]
            return {
                "response_text": f"{party['name']} is part of the {party.get('alliance', 'Unknown Alliance')}.",
                "intent": intent,
                "data": party
            }
            
        if intent == "HISTORY_QUERY":
            party = self.parties[data_key]
            history_text = f"{party['name']} Ruling History:\n"
            ruling_years = party.get("ruling_years", [])
            if ruling_years:
                for term in ruling_years:
                    history_text += f"- {term['from']} to {term['to']}\n"
            else:
                history_text += "No ruling history in Tamil Nadu (as a major ruling party)."
            return {
                "response_text": history_text,
                "intent": intent,
                "data": party
            }

        if intent == "PROPOSED_CM_QUERY":
            party = self.parties[data_key]
            return {
                "response_text": f"The proposed CM candidate for {party['name']} is {party['proposed_cm']}.",
                "intent": intent,
                "data": party
            }
            
        if intent == "LEADER_INFO":
            party = self.parties[data_key]
            # Since we matched a leader name, let's just return general leader info
            leaders_str = ", ".join(party.get("leaders", [party["proposed_cm"]]))
            return {
                 "response_text": f"{party['name']} Key Leaders: {leaders_str}.",
                 "intent": intent,
                 "data": party
            }

        if intent == "SYMBOL_QUERY":
            party = self.parties[data_key]
            return {
                "response_text": f"The symbol of {party['name']} is {party['symbol']}.",
                "intent": intent,
                "data": party
            }
            
        if intent == "SYMBOL_IDENTIFICATION":
            party = self.parties[data_key]
            return {
                "response_text": f"Party Name: {party['name']}",
                "intent": intent,
                "data": party
            }
            
        if intent == "PARTY_INFO":
            party = self.parties[data_key]
            info = f"{party['name']} ({party['full_name']})\n"
            info += f"Symbol: {party['symbol']}\n"
            info += f"Leader/CM Candidate: {party['proposed_cm']}\n"
            if "founder" in party:
                info += f"Founder: {party['founder']} ({party.get('founded_year', 'Unknown')})\n"
            if "alliance" in party:
                info += f"Alliance: {party['alliance']}"
            return {
                "response_text": info,
                "intent": intent,
                "data": party
            }

        return {
            "response_text": "I understood this is about the election, but I couldn't identify the specific question. Try asking about a party symbol, slogan, CM candidate, founder, or alliance.",
            "intent": intent
        }

    def get_suggestions(self, query: str):
        query = query.lower()
        suggestions = []
        
        # Suggest Party Names
        for party in self.parties.keys():
            if query in party.lower():
                suggestions.append(party)
        
        # Suggest Leaders
        for party in self.parties.values():
            if query in party["proposed_cm"].lower():
                suggestions.append(party["proposed_cm"])
                
        # Suggest Symbols
        for party in self.parties.values():
            if query in party["symbol"].lower():
                 suggestions.append(party["symbol"])
                 
        return list(set(suggestions))[:5] # Return top 5 unique suggestions
