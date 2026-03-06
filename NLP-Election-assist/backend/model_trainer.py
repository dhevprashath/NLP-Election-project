import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import joblib
import os
from data import PARTIES, ELECTION_KEYWORDS

# 1. Define Intents
INTENTS = [
    "SLOGAN_QUERY",
    "FOUNDER_QUERY",
    "ALLIANCE_QUERY",
    "HISTORY_QUERY",
    "PROPOSED_CM_QUERY",
    "SYMBOL_QUERY",
    "PARTY_INFO",
    "LEADER_INFO",
    "SONG_QUERY"
]

def generate_training_data():
    data = []
    
    for party_key, info in PARTIES.items():
        name = info['name']
        full_name = info['full_name']
        cm = info['cm_candidate_tn']
        symbol = info['symbol']
        founder = info.get('founder', 'Unknown')
        
        # Slogan queries
        for slogan in info['slogans']:
            data.append({"text": f"what is the slogan of {name}?", "label": "SLOGAN_QUERY"})
            data.append({"text": f"tell me {full_name} slogan", "label": "SLOGAN_QUERY"})
            data.append({"text": slogan, "label": "SLOGAN_QUERY"})
            data.append({"text": f"who said {slogan}?", "label": "SLOGAN_QUERY"})

        # Founder queries
        data.append({"text": f"who founded {name}?", "label": "FOUNDER_QUERY"})
        data.append({"text": f"who is the founder of {full_name}?", "label": "FOUNDER_QUERY"})
        data.append({"text": f"when was {name} started?", "label": "FOUNDER_QUERY"})
        data.append({"text": f"{founder} founded which party?", "label": "FOUNDER_QUERY"})

        # Alliance queries
        data.append({"text": f"what is the alliance of {name}?", "label": "ALLIANCE_QUERY"})
        data.append({"text": f"is {full_name} in nda or india alliance?", "label": "ALLIANCE_QUERY"})
        data.append({"text": f"{name} partners", "label": "ALLIANCE_QUERY"})

        # History queries
        data.append({"text": f"history of {name}", "label": "HISTORY_QUERY"})
        data.append({"text": f"how many years did {full_name} rule?", "label": "HISTORY_QUERY"})
        data.append({"text": f"past governments of {name}", "label": "HISTORY_QUERY"})

        # Proposed CM queries
        data.append({"text": f"who is the cm candidate for {name}?", "label": "PROPOSED_CM_QUERY"})
        data.append({"text": f"proposed chief minister of {full_name}", "label": "PROPOSED_CM_QUERY"})
        data.append({"text": f"is {cm} the next cm?", "label": "PROPOSED_CM_QUERY"})

        # Symbol queries
        data.append({"text": f"what is the symbol of {name}?", "label": "SYMBOL_QUERY"})
        data.append({"text": f"show me {full_name} symbol", "label": "SYMBOL_QUERY"})
        data.append({"text": f"which party has {symbol} symbol?", "label": "SYMBOL_QUERY"})
        data.append({"text": symbol, "label": "SYMBOL_QUERY"})

        # Song queries
        data.append({"text": f"play {name} song", "label": "SONG_QUERY"})
        data.append({"text": f"what is the anthem of {full_name}?", "label": "SONG_QUERY"})
        data.append({"text": f"{name} election music", "label": "SONG_QUERY"})
        data.append({"text": f"youtube link for {name} song", "label": "SONG_QUERY"})

        # Party Info
        data.append({"text": f"tell me about {name}", "label": "PARTY_INFO"})
        data.append({"text": f"details of {full_name}", "label": "PARTY_INFO"})
        data.append({"text": f"who is {name}?", "label": "PARTY_INFO"})

        # Leader Info
        leaders_to_train = info.get('leaders', [])
        
        # Also include names from leadership and important roles if they exist
        if 'leadership' in info:
            leaders_to_train.extend(info['leadership'].values())
        if 'important_roles_in_party' in info:
            leaders_to_train.extend([r['name'] for r in info['important_roles_in_party']])
        
        # Deduplicate names
        leaders_to_train = list(set(leaders_to_train))

        for leader in leaders_to_train:
            data.append({"text": f"who is {leader}?", "label": "LEADER_INFO"})
            data.append({"text": f"tell me about {leader}", "label": "LEADER_INFO"})
            data.append({"text": f"{leader} belongs to which party?", "label": "LEADER_INFO"})

    return pd.DataFrame(data)

def train_model():
    print("Generating training data...")
    df = generate_training_data()
    
    print(f"Training on {len(df)} samples...")
    
    # Create a pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
        ('clf', LogisticRegression(C=10, solver='liblinear'))
    ])
    
    pipeline.fit(df['text'], df['label'])
    
    # Save the model
    model_path = 'intent_model.joblib'
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
