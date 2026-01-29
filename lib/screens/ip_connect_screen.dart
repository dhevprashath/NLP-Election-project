import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import 'splash_screen.dart';

class IpConnectScreen extends StatefulWidget {
  const IpConnectScreen({super.key});

  @override
  State<IpConnectScreen> createState() => _IpConnectScreenState();
}

class _IpConnectScreenState extends State<IpConnectScreen> {
  // Pre-filling with the user's specific LAN IP for convenience
  final TextEditingController _ipController =
      TextEditingController(text: '10.201.80.222');

  Future<void> _connect() async {
    final String ip = _ipController.text.trim();

    if (ip.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a valid IP address'),
          backgroundColor: Colors.redAccent,
        ),
      );
      return;
    }

    // Save IP to SharedPreferences
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('system_ip', ip);

    // Update ApiService Base URL
    ApiService.updateBaseUrl(ip);

    if (!mounted) return;

    // Navigate to Main App (SplashScreen)
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (context) => const SplashScreen()),
    );
  }

  @override
  void dispose() {
    _ipController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Connect to Server',
                style: GoogleFonts.poppins(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue[800],
                ),
              ),
              const SizedBox(height: 30),
              TextField(
                controller: _ipController,
                decoration: InputDecoration(
                  hintText: 'Enter System IP Address',
                  hintStyle: GoogleFonts.poppins(color: Colors.grey),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: Colors.blue[800]!),
                  ),
                  prefixIcon: const Icon(Icons.computer),
                ),
                keyboardType: TextInputType.number,
                style: GoogleFonts.poppins(),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _connect,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[800],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    'CONNECT',
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
