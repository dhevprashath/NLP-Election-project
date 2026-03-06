import 'package:flutter/material.dart';
import 'dart:async';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import 'package:url_launcher/url_launcher.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final GlobalKey<AnimatedListState> _listKey = GlobalKey<AnimatedListState>();
  final ApiService _apiService = ApiService();
  final stt.SpeechToText _speech = stt.SpeechToText();
  final FocusNode _focusNode = FocusNode();

  Future<void> _launchURL(String url) async {
    final Uri uri = Uri.parse(url);
    if (!await launchUrl(uri)) {
      debugPrint("Could not launch $url");
    }
  }

  final List<Message> _messages = [];
  List<String> _suggestions = [];
  bool _isListening = false;
  bool _isLoading = false;
  bool _showSuggestions = false;
  Timer? _debounce;
  Timer? _speechTimeout;

  @override
  void initState() {
    super.initState();
    _addInitialMessage();
    _initSpeech();
  }

  void _addInitialMessage() {
    final initialMessage = Message(
      text:
          "Hello! I am your Election Campaign Assistant. Ask me about party slogans, symbols, or candidates.",
      isUser: false,
    );
    _messages.add(initialMessage);
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _speechTimeout?.cancel();
    _textController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _initSpeech() async {
    try {
      await _speech.initialize(
        onError: (val) => debugPrint('STT Error: $val'),
        onStatus: (val) {
          if (val == 'done' || val == 'notListening') {
            setState(() => _isListening = false);
          }
        },
      );
    } catch (e) {
      debugPrint("Speech init error: $e");
    }
  }

  void _listen() async {
    if (!_isListening) {
      if (!_speech.isAvailable) {
        bool available = await _speech.initialize();
        if (!available) return;
      }

      setState(() => _isListening = true);
      _speech.listen(
        onResult: (val) {
          setState(() {
            _textController.text = val.recognizedWords;
          });

          _onTextChanged(val.recognizedWords);

          // Custom auto-submission timeout
          _speechTimeout?.cancel();
          if (val.recognizedWords.trim().isNotEmpty) {
            _speechTimeout = Timer(const Duration(milliseconds: 3000), () {
              if (_isListening) {
                _sendMessage(val.recognizedWords);
                _speech.stop();
                setState(() => _isListening = false);
              }
            });
          }

          // Auto-send when final result is received
          if (val.finalResult && val.recognizedWords.trim().isNotEmpty) {
            _speechTimeout?.cancel();
            _sendMessage(val.recognizedWords);
            _speech.stop();
          }
        },
        listenFor: const Duration(seconds: 30),
        pauseFor: const Duration(milliseconds: 3000),
        partialResults: true,
        listenMode: stt.ListenMode.confirmation,
      );
    } else {
      _speech.stop();
      setState(() => _isListening = false);
    }
  }

  void _addMessage(Message message) {
    _messages.add(message);
    _listKey.currentState?.insertItem(_messages.length - 1,
        duration: const Duration(milliseconds: 500));
    _scrollToBottom();
  }

  void _sendMessage([String? text]) async {
    final msgText = text ?? _textController.text.trim();
    if (msgText.isEmpty) return;

    _addMessage(Message(text: msgText, isUser: true));

    setState(() {
      _isLoading = true;
      _textController.clear();
      _suggestions = [];
      _showSuggestions = false;
    });

    // Keep the input field focused
    _focusNode.requestFocus();

    // Check for Flag or Logo request
    String lowerMsg = msgText.toLowerCase();
    Map<String, List<String>> partyAliases = {
      "AIADMK": ["aiadmk", "admk", "two leaves", "eps"],
      "DMK": ["dmk", "rising sun", "stalin"],
      "BJP": ["bjp", "lotus", "annamalai", "modi"],
      "INC": ["congress", "inc", "hand", "rahul"],
      "NTK": ["ntk", "tiger", "seeman"],
      "TVK": [
        "tvk",
        "tvke",
        "tv ke",
        "vijay",
        "thalapathy",
        "yellow and red flag"
      ],
      "CPI": ["cpi", "communist", "comunist", "hammer and sickle"],
    };

    Map<String, String> partyFlagAssets = {
      "AIADMK": "assets/images/aiadmk_flag.png",
      "DMK": "assets/images/dmk_flag.png",
      "BJP": "assets/images/bjp_flag.png",
      "INC": "assets/images/congress_flag.png",
      "NTK": "assets/images/ntk_flag.png",
      "TVK": "assets/images/tvk_flag.png",
      "CPI": "assets/images/cpi_flag.png",
    };

    Map<String, String> partyLogoAssets = {
      "CPI": "assets/images/cpi_logo.png",
    };

    String? foundPartyId;
    String? foundAssetPath;
    String assetType = "flag";

    if (lowerMsg.contains("flag") ||
        lowerMsg.contains("logo") ||
        lowerMsg.contains("symbol")) {
      for (var entry in partyAliases.entries) {
        for (var alias in entry.value) {
          if (lowerMsg.contains(alias)) {
            foundPartyId = entry.key;
            break;
          }
        }
        if (foundPartyId != null) break;
      }

      if (foundPartyId != null) {
        if (lowerMsg.contains("logo") || lowerMsg.contains("symbol")) {
          assetType = "logo";
          foundAssetPath =
              partyLogoAssets[foundPartyId] ?? partyFlagAssets[foundPartyId];
        } else {
          assetType = "flag";
          foundAssetPath = partyFlagAssets[foundPartyId];
        }
      }
    }

    if (foundAssetPath != null) {
      await Future.delayed(const Duration(milliseconds: 800));
      setState(() => _isLoading = false);
      _addMessage(Message(
        text: "Here is the $assetType of $foundPartyId:",
        isUser: false,
        imagePath: foundAssetPath,
        intent: "SHOW_FLAG",
      ));
      return;
    }

    try {
      final response = await _apiService.sendMessage(msgText);
      setState(() => _isLoading = false);

      String? imageUrl;
      if (response['data'] != null && response['data']['image_url'] != null) {
        imageUrl = response['data']['image_url'];
      }

      _addMessage(Message(
        text: response['response_text'],
        isUser: false,
        intent: response['detected_intent'],
        imageUrl: imageUrl,
      ));
    } catch (e) {
      setState(() => _isLoading = false);
      _addMessage(
          Message(text: "Error: Could not connect to server.", isUser: false));
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
    Future.delayed(const Duration(milliseconds: 300), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeOutCubic,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Text("Election Assistant",
            style: GoogleFonts.outfit(
                fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Colors.blue[900]!, Colors.blue[600]!, Colors.blue[400]!],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Expanded(
                child: AnimatedList(
                  key: _listKey,
                  controller: _scrollController,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                  initialItemCount: _messages.length,
                  itemBuilder: (context, index, animation) {
                    return _buildAnimatedMessageBubble(
                        _messages[index], animation);
                  },
                ),
              ),
              if (_isLoading)
                const Padding(
                  padding: EdgeInsets.only(bottom: 12.0),
                  child: SpinKitPulse(color: Colors.white70, size: 30),
                ),
              _buildInputArea(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnimatedMessageBubble(Message msg, Animation<double> animation) {
    return SizeTransition(
      sizeFactor: animation,
      child: FadeTransition(
        opacity: animation,
        child: SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0, 0.2),
            end: Offset.zero,
          ).animate(
              CurvedAnimation(parent: animation, curve: Curves.easeOutQuad)),
          child: _buildMessageBubble(msg),
        ),
      ),
    );
  }

  Widget _buildMessageBubble(Message msg) {
    final bool isUser = msg.isUser;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Align(
        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
        child: Column(
          crossAxisAlignment:
              isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
              decoration: BoxDecoration(
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  )
                ],
                gradient: isUser
                    ? const LinearGradient(
                        colors: [Colors.white, Color(0xFFF5F7FA)])
                    : LinearGradient(
                        colors: [Colors.blue[800]!, Colors.blue[900]!]),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(20),
                  topRight: const Radius.circular(20),
                  bottomLeft: isUser ? const Radius.circular(20) : Radius.zero,
                  bottomRight: isUser ? Radius.zero : const Radius.circular(20),
                ),
              ),
              constraints: BoxConstraints(
                  maxWidth: MediaQuery.of(context).size.width * 0.8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (msg.imagePath != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 10.0),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.asset(msg.imagePath!, fit: BoxFit.cover),
                      ),
                    ),
                  if (msg.imageUrl != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 10.0),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.network(
                          "${ApiService.baseUrl}${msg.imageUrl}",
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return const Icon(Icons.broken_image,
                                color: Colors.white24, size: 50);
                          },
                        ),
                      ),
                    ),
                  _buildMessageText(msg, isUser),
                ],
              ),
            ),
            if (!isUser && msg.intent != null && msg.intent != "OUT_OF_DOMAIN")
              Padding(
                padding: const EdgeInsets.only(top: 6, left: 4),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.white24,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    msg.intent!.replaceAll("_", " "),
                    style: GoogleFonts.inter(
                      fontSize: 9,
                      fontWeight: FontWeight.w600,
                      color: Colors.white70,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_showSuggestions) _buildSuggestionsList(),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(30),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 20,
                  offset: const Offset(0, 4),
                )
              ],
            ),
            child: Row(
              children: [
                const SizedBox(width: 8),
                IconButton(
                  icon: Icon(_isListening ? Icons.mic : Icons.mic_none,
                      color: _isListening ? Colors.red : Colors.blueGrey),
                  onPressed: _listen,
                ),
                Expanded(
                  child: TextField(
                    controller: _textController,
                    focusNode: _focusNode,
                    autofocus: true,
                    onChanged: _onTextChanged,
                    onSubmitted: (val) => _sendMessage(),
                    style: const TextStyle(color: Colors.black87, fontSize: 16),
                    decoration: InputDecoration(
                      hintText: "Ask about elections...",
                      hintStyle: GoogleFonts.poppins(
                          color: Colors.grey[400], fontSize: 15),
                      border: InputBorder.none,
                      contentPadding:
                          const EdgeInsets.symmetric(horizontal: 12),
                    ),
                  ),
                ),
                GestureDetector(
                  onTap: () => _sendMessage(),
                  child: Container(
                    margin: const EdgeInsets.all(6),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                          colors: [Colors.blue[700]!, Colors.blue[900]!]),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.send_rounded,
                        color: Colors.white, size: 22),
                  ),
                ),
                const SizedBox(width: 4),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionsList() {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 10)],
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxHeight: 180),
        child: ListView.builder(
          shrinkWrap: true,
          itemCount: _suggestions.length,
          itemBuilder: (ctx, i) {
            return ListTile(
              dense: true,
              visualDensity: VisualDensity.compact,
              title: Text(_suggestions[i],
                  style: GoogleFonts.poppins(fontSize: 14)),
              onTap: () {
                _textController.text = _suggestions[i];
                _sendMessage(_suggestions[i]);
                setState(() => _showSuggestions = false);
              },
            );
          },
        ),
      ),
    );
  }

  Widget _buildMessageText(Message msg, bool isUser) {
    final style = GoogleFonts.poppins(
      height: 1.4,
      fontSize: 15,
      color: isUser ? Colors.blue[900] : Colors.white.withOpacity(0.95),
      fontWeight: isUser ? FontWeight.w500 : FontWeight.w400,
    );

    // Detect YouTube links or any URL
    final urlRegExp = RegExp(r'(https?://[^\s]+)');
    final matches = urlRegExp.allMatches(msg.text);

    if (matches.isEmpty) {
      return Text(msg.text, style: style);
    }

    // Since TextSpan recognizers can be tricky, we'll check if it's a SONG_QUERY
    // and provide a dedicated button if needed.
    return Column(
      crossAxisAlignment:
          isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
      children: [
        Text(msg.text, style: style),
        if (matches.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8.0),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(20),
                onTap: () {
                  debugPrint("Tapped link: ${matches.first.group(0)}");
                  _launchURL(matches.first.group(0)!);
                },
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: isUser ? Colors.blue[50] : Colors.white12,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                        color: isUser ? Colors.blue[100]! : Colors.white24),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.play_circle_fill,
                          color: Colors.red, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        "Watch on YouTube",
                        style: GoogleFonts.poppins(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: isUser ? Colors.blue[900] : Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
