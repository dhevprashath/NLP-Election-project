class Message {
  final String text;
  final bool isUser;
  final String? intent; // Optional, for debugging or UI hints
  final String? imagePath;
  final String? imageUrl;

  Message({
    required this.text,
    required this.isUser,
    this.intent,
    this.imagePath,
    this.imageUrl,
  });
}
