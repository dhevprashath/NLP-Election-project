# Election Assistant App - Setup & Run Instructions

This project consists of a **Python FastAPI Backend** and a **Flutter Frontend**.

## Prerequisites
- **Python 3.8+** installed.
- **Flutter SDK** installed and configured (check via `flutter doctor`).
- **Android Studio** (for Android Emulator) or an attached physical device.
- **Git** (optional, for cloning).

---

## 🚀 1. Backend Setup (FastAPI)

The backend handles the NLP logic and party data.

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create a virtual environment (Recommended):**
    ```sh
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    *(If you face issues, manually install: `pip install fastapi uvicorn pydantic requests`)*

4.  **Run the Server:**
    ```sh
    python main.py
    ```
    *The server will start at `http://0.0.0.0:8000`. Auto-reload is enabled.*

    **Verify it's working:**
    Open your browser to [http://localhost:8000/](http://localhost:8000/) or [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

---

## 📱 2. Frontend Setup (Flutter)

The frontend is a mobile app communicating with the backend.

1.  **Navigate to the app directory:**
    ```sh
    cd frontend/election_assistant_app
    ```

2.  **Install dependencies:**
    ```sh
    flutter pub get
    ```

3.  **Run the App:**
    Make sure a device is connected or emulator is running.
    ```sh
    flutter run
    ```
    
    **To run on Chrome (Web):**
    ```sh
    flutter run -d chrome
    ```

---

## 🔧 Troubleshooting

### Connection Refused (Android Emulator)
If running on Android Emulator, the backend URL in Dart code must be `http://10.0.2.2:8000` instead of `localhost`.
- Check `lib/api_service.dart` (or equivalent config file) to ensure the URL matches your environment.

### Backend not reloading?
- Ensure you are running `python main.py` which now includes `reload=True`.

### Missing Keywords/Data?
- If the bot doesn't understand "Alliance" or "Founder", ensure `data.py` and `nlp_engine.py` are up to date (restart backend if needed).
