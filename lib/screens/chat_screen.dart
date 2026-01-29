import 'package:flutter/material.dart';
import 'dart:async';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../models/message.dart';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ApiService _apiService = ApiService();
  final stt.SpeechToText _speech = stt.SpeechToText();

  List<Message> _messages = [];
  List<String> _suggestions = [];
  bool _isListening = false;
  bool _isLoading = false;
  bool _showSuggestions = false;
  Timer? _debounce;

  @override
  void initState() {
    super.initState();
    _messages.add(Message(
      text:
          "Hello! I am your Election Campaign Assistant. Ask me about party slogans, symbols, or candidates.",
      isUser: false,
    ));
    _initSpeech();
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _initSpeech() async {
    try {
      await _speech.initialize();
    } catch (e) {
      debugPrint("Speech init error: $e");
    }
  }

  void _listen() async {
    if (!_isListening) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (val) {
            setState(() {
              _textController.text = val.recognizedWords;
              if (val.hasConfidenceRating && val.confidence > 0) {
                // optional: show confidence
              }
            });
            _onTextChanged(val.recognizedWords);
          },
        );
      }
    } else {
      setState(() => _isListening = false);
      _speech.stop();
    }
  }

  void _sendMessage([String? text]) async {
    final msgText = text ?? _textController.text.trim();
    if (msgText.isEmpty) return;

    setState(() {
      _messages.add(Message(text: msgText, isUser: true));
      _isLoading = true;
      _textController.clear();
      _suggestions = [];
      _showSuggestions = false;
    });
    _scrollToBottom();

    // Check for Flag request
    String lowerMsg = msgText.toLowerCase();
    Map<String, String> partyFlags = {
      "aiadmk": "assets/images/aiadmk_flag.png",
      "admk": "assets/images/aiadmk_flag.png",
      "ntk": "assets/images/ntk_flag.png",
      "naam tamilar katchi": "assets/images/ntk_flag.png",
      "tvk": "assets/images/tvk_flag.png",
      "tamilaga vettri kazhagam": "assets/images/tvk_flag.png",
      "dmk": "assets/images/dmk_flag.png",
      "dravida munnetra kazhagam": "assets/images/dmk_flag.png",
      "bjp": "assets/images/bjp_flag.png",
      "bharatiya janata party": "assets/images/bjp_flag.png",
      "congress": "assets/images/congress_flag.png",
      "inc": "assets/images/congress_flag.png",
    };

    String? foundParty;
    String? foundFlagPath;

    if (lowerMsg.contains("flag")) {
      for (var entry in partyFlags.entries) {
        if (lowerMsg.contains(entry.key)) {
          foundParty = entry.key.toUpperCase();
          foundFlagPath = entry.value;
          break;
        }
      }
    }

    if (foundFlagPath != null) {
      // Simulate network delay
      await Future.delayed(const Duration(milliseconds: 500));

      setState(() {
        _messages.add(Message(
          text: "Here is the flag of $foundParty:",
          isUser: false,
          imagePath: foundFlagPath,
          intent: "SHOW_FLAG",
        ));
        _isLoading = false;
      });
      _scrollToBottom();
      return;
    }

    // Check for Party History / Leader info
    Map<String, String> partyHistory = {
      "aiadmk":
          "AIADMK Leaders History:\n1. M.G. Ramachandran (Founder)\n2. J. Jayalalithaa\n3. Edappadi K. Palaniswami (General Secretary)",
      "dmk":
          "DMK Leaders History:\n1. C.N. Annadurai (Founder)\n2. M. Karunanidhi\n3. M.K. Stalin (Current)",
      "ntk": "Naam Tamilar Katchi Leaders:\n1. Seeman (Chief Coordinator)",
      "tvk": "Tamilaga Vettri Kazhagam Leaders:\n1. Vijay (President)",
      "bjp":
          "BJP Tamil Nadu Presidents (Recent):\n1. Tamilisai Soundararajan\n2. L. Murugan\n3. K. Annamalai (Current)",
      "congress":
          "TN Congress Committee Presidents (Recent):\n1. E.V.K.S. Elangovan\n2. Su. Thirunavukkarasar\n3. K.S. Alagiri\n4. K. Selvaperunthagai (Current)",
    };

    Map<String, String> leaderInfo = {
      "stalin":
          "M.K. Stalin is the Chief Minister of Tamil Nadu and the President of the Dravida Munnetra Kazhagam (DMK). He is the son of former CM M. Karunanidhi.",
      "mk stalin":
          "M.K. Stalin is the Chief Minister of Tamil Nadu and the President of the Dravida Munnetra Kazhagam (DMK). He is the son of former CM M. Karunanidhi.",
      "eps":
          "Edappadi K. Palaniswami (EPS) is the General Secretary of the All India Anna Dravida Munnetra Kazhagam (AIADMK) and served as the 7th Chief Minister of Tamil Nadu.",
      "palaniswami":
          "Edappadi K. Palaniswami (EPS) is the General Secretary of the All India Anna Dravida Munnetra Kazhagam (AIADMK) and served as the 7th Chief Minister of Tamil Nadu.",
      "seeman":
          "Seeman is the Chief Coordinator of the Naam Tamilar Katchi (NTK). He is a film director turned politician known for his Tamil nationalist ideology.",
      "vijay":
          "Vijay is a popular actor and the President of the newly formed Tamilaga Vettri Kazhagam (TVK). He entered politics in 2024.",
      "thalapathy":
          "Vijay is a popular actor and the President of the newly formed Tamilaga Vettri Kazhagam (TVK). He entered politics in 2024.",
      "annamalai":
          "K. Annamalai is the State President of the Bharatiya Janata Party (BJP) in Tamil Nadu. He is a former IPS officer.",
    };

    String? responseText;
    String? intent;

    // Check History first
    if (lowerMsg.contains("history") ||
        lowerMsg.contains("previous") ||
        (lowerMsg.contains("leaders") && !lowerMsg.contains("who"))) {
      for (var entry in partyHistory.entries) {
        if (lowerMsg.contains(entry.key)) {
          responseText = entry.value;
          intent = "Get_Party_History"; // Custom intent
          break;
        }
      }
    }

    // Check Leader details if no history found
    if (responseText == null) {
      for (var entry in leaderInfo.entries) {
        if (lowerMsg.contains(entry.key)) {
          responseText = entry.value;
          intent = "Get_Candidate_Details";
          break;
        }
      }
    }

    if (responseText != null) {
      // Simulate network delay
      await Future.delayed(const Duration(milliseconds: 500));
      setState(() {
        _messages.add(Message(
          text: responseText!,
          isUser: false,
          intent: intent,
        ));
        _isLoading = false;
      });
      _scrollToBottom();
      return;
    }

    try {
      final response = await _apiService.sendMessage(msgText);
      setState(() {
        _messages.add(Message(
          text: response['response_text'],
          isUser: false,
          intent: response['detected_intent'],
        ));
      });
    } catch (e) {
      setState(() {
        _messages.add(Message(
          text: "Error: Could not connect to server.",
          isUser: false,
        ));
      });
    } finally {
      setState(() => _isLoading = false);
      _scrollToBottom();
    }
  }

  void _onTextChanged(String value) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();

    _debounce = Timer(const Duration(milliseconds: 300), () async {
      if (value.isEmpty) {
        setState(() => _showSuggestions = false);
        return;
      }

      final suggestions = await _apiService.getSuggestions(value);
      setState(() {
        _suggestions = suggestions;
        _showSuggestions = suggestions.isNotEmpty;
      });
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Election Assistant",
            style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue[900],
        elevation: 0,
      ),
      backgroundColor: Colors.blue,
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: SpinKitThreeBounce(color: Colors.lightBlue, size: 20),
            ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(Message msg) {
    return Align(
      alignment: msg.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: msg.isUser ? Colors.white : Colors.blue[800],
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: msg.isUser ? const Radius.circular(16) : Radius.zero,
            bottomRight: msg.isUser ? Radius.zero : const Radius.circular(16),
          ),
        ),
        constraints:
            BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (msg.imagePath != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.asset(
                    msg.imagePath!,
                    fit: BoxFit.cover,
                    width: 200, // Adjust as needed
                  ),
                ),
              ),
            Text(
              msg.text,
              style: GoogleFonts.poppins(
                color: msg.isUser ? Colors.blue[900] : Colors.white,
              ),
            ),
            if (!msg.isUser &&
                msg.intent != null &&
                msg.intent != "OUT_OF_DOMAIN")
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  "Intent: ${msg.intent}",
                  style: const TextStyle(fontSize: 10, color: Colors.grey),
                ),
              )
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (_showSuggestions)
          Container(
            color: Theme.of(context).colorScheme.surface,
            constraints: const BoxConstraints(maxHeight: 150),
            child: ListView.separated(
              itemCount: _suggestions.length,
              separatorBuilder: (ctx, i) => const Divider(height: 1),
              itemBuilder: (ctx, i) {
                return ListTile(
                  dense: true,
                  title: Text(_suggestions[i]),
                  onTap: () {
                    _textController.text = _suggestions[i];
                    _sendMessage(_suggestions[i]);
                    setState(() => _showSuggestions = false);
                  },
                );
              },
            ),
          ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, -5),
              ),
            ],
          ),
          child: Row(
            children: [
              IconButton(
                icon: Icon(
                  _isListening ? Icons.mic : Icons.mic_none,
                  color: _isListening ? Colors.red : Colors.grey,
                ),
                onPressed: _listen,
              ),
              Expanded(
                child: TextField(
                  controller: _textController,
                  autofocus: true,
                  onChanged: _onTextChanged,
                  decoration: InputDecoration(
                    hintText: "Ask about elections...",
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    border: InputBorder.none,
                  ),
                  style: const TextStyle(color: Colors.black),
                  onSubmitted: _sendMessage,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.send, color: Colors.lightBlue),
                onPressed: () => _sendMessage(),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
