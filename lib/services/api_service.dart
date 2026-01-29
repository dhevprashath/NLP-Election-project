import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // 10.0.2.2 is the localhost alias for Android Emulator
  // If running on a real device via USB, you might need your PC's LAN IP (e.g., 192.168.1.x)
  // Use localhost for Web/Windows. For Android Emulator use 10.0.2.2
  static String baseUrl = 'http://10.201.80.222:8000';

  static void updateBaseUrl(String ip) {
    baseUrl = 'http://$ip:8000';
  }

  Future<Map<String, dynamic>> sendMessage(String message) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_message': message}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load response');
      }
    } catch (e) {
      throw Exception('Error connecting to server: $e');
    }
  }

  Future<List<String>> getSuggestions(String query) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/suggestions?q=$query'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['suggestions']);
      } else {
        return [];
      }
    } catch (e) {
      // Fail silently for suggestions
      return [];
    }
  }
}
