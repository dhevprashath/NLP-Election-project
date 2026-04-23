
from nlp_engine import NLPEngine

def test_query(query):
    engine = NLPEngine()
    response = engine.get_response(query)
    print(f"Query: {query}")
    print(f"Intent: {response.get('intent')}")
    print(f"Response: {response.get('response_text')}")
    print("-" * 20)

if __name__ == "__main__":
    test_query("DMK ruling years")
    test_query("AIADMK history")
    test_query("how many years did congress rule?")
    test_query("BJP ruling history")
