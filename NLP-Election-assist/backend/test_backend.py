from nlp_engine import NLPEngine

def test_nlp():
    nlp = NLPEngine()
    
    # Test 1: Slogan Detection
    res = nlp.get_response("Dravidam means development")
    assert res["intent"] == "SLOGAN_DETECTED"
    assert res["data"]["name"] == "DMK"
    print("Test 1 Passed: Slogan Detection")

    # Test 2: Symbol Identification
    res = nlp.get_response("Which party has Two Leaves symbol?")
    assert res["intent"] == "SYMBOL_IDENTIFICATION" or res["intent"] == "SYMBOL_QUERY"
    assert res["data"]["name"] == "AIADMK"
    print("Test 2 Passed: Symbol Identification")
    
    # Test 3: Proposed CM
    res = nlp.get_response("Who is the proposed CM of DMK?")
    assert res["intent"] == "PROPOSED_CM_QUERY" or res["intent"] == "LEADER_INFO"
    assert "Stalin" in res["response_text"]
    print("Test 3 Passed: CM Query")
    
    # Test 4: Out of Domain
    res = nlp.get_response("Suggest some movies")
    assert res["intent"] == "OUT_OF_DOMAIN"
    print("Test 4 Passed: Out of Domain")
    
    # Test 5: Auto-suggestion
    suggestions = nlp.get_suggestions("Rising")
    assert "Rising Sun" in suggestions
    print("Test 5 Passed: Suggestions")

if __name__ == "__main__":
    test_nlp()
