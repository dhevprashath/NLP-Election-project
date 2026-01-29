PARTIES = {

    "AIADMK": {
        "name": "AIADMK",
        "full_name": "All India Anna Dravida Munnetra Kazhagam",
        "founded_year": 1972,
        "founder": "M. G. Ramachandran",
        "slogans": [
            "amma's rule",
            "amma forever",
            "peace prosperity progress",
            "two leaves for victory"
        ],
        "symbol": "Two Leaves",
        "proposed_cm": "Edappadi K. Palaniswami",
        "leaders": [
            "Edappadi K. Palaniswami",
            "O. Panneerselvam",
            "J. Jayalalithaa"
        ],
        "ruling_years": [
            {"from": 1977, "to": 1987},
            {"from": 1991, "to": 1996},
            {"from": 2001, "to": 2006},
            {"from": 2011, "to": 2021}
        ],
        "mlas": [
            "Edappadi K. Palaniswami",
            "R. B. Udhayakumar",
            "S. P. Velumani"
        ],
        "ministers": [
            "J. Jayalalithaa (Former CM)",
            "Edappadi K. Palaniswami (Former CM)",
            "O. Panneerselvam (Former Deputy CM)"
        ],
        "alliance": "NDA (earlier)"
    },

    "DMK": {
        "name": "DMK",
        "full_name": "Dravida Munnetra Kazhagam",
        "founded_year": 1949,
        "founder": "C. N. Annadurai",
        "slogans": [
            "dravidam means development",
            "kalaignar legacy",
            "son of the soil",
            "rising sun for rising tamil nadu"
        ],
        "symbol": "Rising Sun",
        "proposed_cm": "M. K. Stalin",
        "leaders": [
            "M. K. Stalin",
            "Udhayanidhi Stalin",
            "M. Karunanidhi"
        ],
        "ruling_years": [
            {"from": 1967, "to": 1976},
            {"from": 1989, "to": 1991},
            {"from": 1996, "to": 2001},
            {"from": 2006, "to": 2011},
            {"from": 2021, "to": "Present"}
        ],
        "mlas": [
            "M. K. Stalin",
            "Udhayanidhi Stalin",
            "E. V. Velu"
        ],
        "ministers": [
            "M. K. Stalin (Chief Minister)",
            "Udhayanidhi Stalin (Youth Welfare Minister)",
            "Duraimurugan (Water Resources Minister)"
        ],
        "alliance": "INDIA Alliance"
    },

    "INC": {
        "name": "INC",
        "full_name": "Indian National Congress",
        "founded_year": 1885,
        "founder": "A. O. Hume",
        "slogans": [
            "nyay",
            "bharat jodo",
            "save democracy"
        ],
        "symbol": "Hand",
        "proposed_cm": "Not announced",
        "leaders": [
            "Rahul Gandhi",
            "Sonia Gandhi",
            "K. S. Alagiri"
        ],
        "ruling_years": [
            {"from": 1957, "to": 1962},
            {"from": 1963, "to": 1967}
        ],
        "mlas": [
            "S. Jothimani"
        ],
        "ministers": [
            "Rahul Gandhi (Former MP)",
            "Sonia Gandhi (Former MP)"
        ],
        "alliance": "INDIA Alliance"
    },

    "BJP": {
        "name": "BJP",
        "full_name": "Bharatiya Janata Party",
        "founded_year": 1980,
        "founder": "Syama Prasad Mukherjee",
        "slogans": [
            "nation first",
            "lotus blooms",
            "modi's guarantee"
        ],
        "symbol": "Lotus",
        "proposed_cm": "K. Annamalai",
        "leaders": [
            "K. Annamalai",
            "Narendra Modi",
            "Amit Shah"
        ],
        "ruling_years": [],
        "mlas": [
            "Nainar Nagendran"
        ],
        "ministers": [
            "Narendra Modi (Prime Minister)",
            "Amit Shah (Home Minister)"
        ],
        "alliance": "NDA"
    },

    "PMK": {
        "name": "PMK",
        "full_name": "Pattali Makkal Katchi",
        "founded_year": 1989,
        "founder": "S. Ramadoss",
        "slogans": [
            "social justice",
            "vanniyar rights"
        ],
        "symbol": "Mango",
        "proposed_cm": "Anbumani Ramadoss",
        "leaders": [
            "S. Ramadoss",
            "Anbumani Ramadoss"
        ],
        "ruling_years": [],
        "mlas": [
            "G. K. Mani"
        ],
        "ministers": [
            "Anbumani Ramadoss (Former Union Minister)"
        ],
        "alliance": "NDA (earlier)"
    },

    "DMDK": {
        "name": "DMDK",
        "full_name": "Desiya Murpokku Dravida Kazhagam",
        "founded_year": 2005,
        "founder": "Vijayakanth",
        "slogans": [
            "captain's rule",
            "people welfare"
        ],
        "symbol": "Rising Sun between Hills",
        "proposed_cm": "Not announced",
        "leaders": [
            "Vijayakanth",
            "Premalatha Vijayakanth"
        ],
        "ruling_years": [],
        "mlas": [
            "Vijayakanth"
        ],
        "ministers": [],
        "alliance": "NDA"
    },

    "NTK": {
        "name": "NTK",
        "full_name": "Naam Tamilar Katchi",
        "founded_year": 2010,
        "founder": "Seeman",
        "slogans": [
            "tamil rule for tamils",
            "farming is life"
        ],
        "symbol": "Farmer (Ganna Kisan)",
        "proposed_cm": "Seeman",
        "leaders": ["Seeman"],
        "ruling_years": [],
        "mlas": [],
        "ministers": [],
        "alliance": "Independent"
    },

    "TVK": {
        "name": "TVK",
        "full_name": "Tamizhaga Vettri Kazhagam",
        "founded_year": 2024,
        "founder": "Vijay",
        "slogans": [
            "pirappokkum ella uyirukkum",
            "victory regarding tamil nadu"
        ],
        "symbol": "Two Elephants with Vaagai Flower",
        "proposed_cm": "Vijay",
        "leaders": ["Vijay"],
        "ruling_years": [],
        "mlas": [],
        "ministers": [],
        "alliance": "To be announced"
    }
}

# Domain keywords to quickly filter out obvious out-of-domain queries
ELECTION_KEYWORDS = [
    "party", "slogan", "symbol", "cm", "minister", "vote", "election", 
    "candidate", "poll", "dmk", "aiadmk", "bjp", "ntk", "congress", "tvk", "inc", "pmk", "dmdk",
    "stalin", "edappadi", "annamalai", "seeman", "vijay", "leader", "captain", "vijayakanth", "anbumani",
    "mla", "mp", "politics", "manifesto", "dravidam", "amma", "alliance", "founder", "founded"
]

