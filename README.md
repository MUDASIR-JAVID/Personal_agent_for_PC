# Astra: Desktop Voice-Controlled Assistant Agent

A production-ready, robust, and extensible local desktop voice assistant built in Python for Windows. Powered by **SpeechRecognition**, offline **pyttsx3** (Microsoft SAPI5), and Google's official **Gemini AI** (`google-genai` SDK with `gemini-3.8-flash`).

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows)
![Gemini AI](https://img.shields.io/badge/Gemini%20API-google--genai-8E75C2?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 Core Features

- **🎙️ Real-Time Voice Recognition & Audio Calibration**:
  - Continuous ambient listening with automatic background noise calibration (`adjust_for_ambient_noise`).
  - Dynamic energy thresholding and silence detection (`pause_threshold`).
  - Graceful handling of timeouts, unintelligible audio, and microphone disconnections without ever crashing.

- **🔊 Offline, High-Speed Speech Synthesis (TTS)**:
  - Powered by Windows Microsoft SAPI5 (`pyttsx3`) for instant, offline, zero-latency vocal responses.
  - Pre-configured with crystal-clear voices (Microsoft David and Microsoft Zira).
  - Built-in text cleaner that strips markdown formatting, asterisks, URLs, and code blocks before speaking for fluid speech.

- **💻 Windows System Control & App Launcher**:
  - Secure application launching and termination using Python's `os` and `subprocess` modules (strictly avoiding vulnerable `shell=True` string injections).
  - Out-of-the-box support for:
    - **WhatsApp** (desktop URI & path detection)
    - **Google Chrome**
    - **Visual Studio Code**
    - **Notepad**
    - **Calculator**
    - **File Explorer**
    - **Task Manager**, **Paint**, **Windows Settings**, and more.

- **🌐 Web Controller & Search Automation**:
  - Search Google, YouTube, GitHub, or Wikipedia instantly by voice.
  - Open direct websites (e.g., *"open youtube"*, *"open github"*, *"open reddit"*).

- **📝 Desktop Operations, Notes & Telemetry**:
  - **Spoken Time & Date**: Accurate, natural speech output (e.g. *"The current time is 9:15 PM."*).
  - **Voice Notes**: Create and append timestamped notes (`data/notes/`), and read back recent entries.
  - **File Explorer Integration**: List files in user folders (`Downloads`, `Documents`, `Desktop`) and open directories.
  - **Hardware Status**: Real-time battery percentage, AC adapter status, CPU load, and RAM telemetry via `psutil`.

- **🧠 Google Gemini AI Integration**:
  - Modern Gemini GenAI SDK (`google-genai` >= 2.25.0) with default model `gemini-3.8-flash`.
  - Intelligently answers complex reasoning tasks, explanations, knowledge questions, and conversational banter.
  - Tailored system instructions for spoken brevity: concise 1–3 sentence spoken outputs without markdown noise.
  - Resilient design: if the API key is not yet set, all local system commands, app launchers, and tools continue functioning seamlessly.

- **🛡️ Dual Interaction Modes & Robust Stability**:
  - **Voice Mode**: Hands-free voice operation using your laptop microphone.
  - **Interactive Text Mode (`--text`)**: Console interface for silent environments, debugging, or systems without a microphone.
  - Optional Wake Word trigger mode (`--wake-word`).

---

## 📁 Project Structure

```text
voice-assistant/
├── .env.example              # Environment variables template (API keys, voice settings)
├── .gitignore                # Git ignore rules (hides .env, .venv, notes, audio cache)
├── requirements.txt          # Python dependencies
├── README.md                 # Complete documentation and setup guide
├── main.py                   # CLI entry point (voice, text, diagnostic flags)
├── src/
│   ├── __init__.py
│   ├── config.py             # Configuration management and application mappings
│   ├── speech/
│   │   ├── __init__.py
│   │   ├── recognizer.py     # SpeechRecognition audio capture and noise calibration
│   │   └── synthesizer.py    # pyttsx3 SAPI5 TTS engine and text sanitization
│   ├── system/
│   │   ├── __init__.py
│   │   ├── app_launcher.py   # Windows app discovery and secure subprocess execution
│   │   ├── web_controller.py # Browser navigation and Google/YouTube search
│   │   └── system_ops.py     # Time, date, notes, file ops, and hardware telemetry
│   ├── ai/
│   │   ├── __init__.py
│   │   └── gemini_client.py  # Google GenAI SDK (gemini-3.8-flash) chat integration
│   ├── core/
│   │   ├── __init__.py
│   │   ├── command_router.py # Local command parsing with Gemini AI fallback
│   │   └── assistant.py      # Main assistant runtime orchestrator
│   └── utils/
│       ├── __init__.py
│       └── logger.py         # Rich terminal output and structured logging
├── data/
│   └── notes/                # Storage directory for voice notes
│       └── .gitkeep
└── tests/
    ├── __init__.py
    ├── test_command_router.py# Unit tests for routing and intent classification
    ├── test_system_ops.py    # Unit tests for time, date, and note taking
    ├── test_app_launcher.py  # Unit tests for Windows executable resolution
    └── test_synthesizer.py   # Unit tests for TTS speech text cleaning
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Windows 10 or 11**
- **Python 3.10+** (Tested on Python 3.11)
- Working microphone and speakers / headphones

### 2. Clone or Navigate to Project
```powershell
cd C:\Users\mudas\.gemini\antigravity\scratch\voice-assistant
```

### 3. Create & Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate in PowerShell
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell script execution is restricted, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Configure Your Gemini API Key
Copy the template file to `.env`:
```powershell
copy .env.example .env
```
Open `.env` in Notepad or VS Code:
```powershell
notepad .env
```
Set your Gemini API key (obtain a free key from [Google AI Studio](https://aistudio.google.com/app/apikey)):
```env
GEMINI_API_KEY=AIzaSyYourActualGeminiApiKeyHere
GEMINI_MODEL=gemini-3.8-flash
ASSISTANT_NAME=Astra
```

---

## 🛠️ Usage & Execution Modes

### 1. Voice Mode (Default)
Run real-time voice listening on your microphone:
```powershell
python main.py
```

### 2. Interactive Text Mode
Run the assistant in console text mode (no microphone required):
```powershell
python main.py --text
```

### 3. Wake Word Mode
Require the assistant name (e.g. *"Astra"*) before processing any command:
```powershell
python main.py --wake-word
```

### 4. Run Self-Diagnostics
Run comprehensive automated health-checks on audio, Windows app paths, and Gemini client:
```powershell
python main.py --test
```

### 5. Inspect Audio Hardware
```powershell
# List available microphone devices and indices
python main.py --list-mics

# List installed SAPI5 text-to-speech voices
python main.py --list-voices
```

---

## 🗣️ Supported Voice Commands

| Category | Example Voice Commands | Action Performed |
| :--- | :--- | :--- |
| **App Launcher** | *"Open Google Chrome"*<br>*"Launch WhatsApp"*<br>*"Start VS Code"*<br>*"Open Notepad"*<br>*"Open Calculator"*<br>*"Close Chrome"* | Launches or closes Windows applications securely via executable paths and URI protocols. |
| **Web & Search** | *"Search Google for quantum computing"*<br>*"Search YouTube for lo-fi beats"*<br>*"Search GitHub for speech recognition"*<br>*"Open YouTube"* / *"Open Reddit"* | Opens your default web browser and executes the search query or opens the target website. |
| **Time & Date** | *"What time is it?"*<br>*"Tell me the current time"*<br>*"What is today's date?"* | Speaks the current time or formatted date with ordinal day. |
| **Notes** | *"Take a note buy groceries at 5 PM"*<br>*"Write a note finish the project report"*<br>*"Read my notes"* | Appends timestamped note to `data/notes/` and reads back recent notes aloud. |
| **Files & System** | *"List files in downloads"*<br>*"Show files in documents"*<br>*"Open downloads folder"*<br>*"System status"* / *"Battery status"* | Reports directory contents, launches File Explorer, or speaks battery % and CPU/RAM usage. |
| **Gemini AI** | *"Explain theory of relativity in two sentences"*<br>*"Who was Alan Turing?"*<br>*"Give me three tips for better sleep"* | Queries Gemini `gemini-3.8-flash` for an intelligent, concise, spoken response. |
| **Control** | *"What can you do?"* / *"Help"*<br>*"Exit"* / *"Quit"* / *"Goodbye"* | Displays feature overview or performs graceful shutdown. |

---

## 🧪 Running Automated Tests

All core modules include unit tests verifying path resolution, speech sanitization, note operations, and command routing:

```powershell
python -m unittest discover tests
```

Expected result:
```text
Ran 18 tests in 0.09s
OK
```

---

## 🔒 Security & Git Readiness

- **API Keys Protected**: The `.env` file containing your `GEMINI_API_KEY` is pre-configured in `.gitignore` and will never be committed.
- **Safe Subprocess Execution**: System commands are invoked using list arguments (`subprocess.Popen([exe_path])`) without shell string interpolation to prevent injection.
- **Git Push Instructions**:
  ```powershell
  # Initialize git repository
  git init

  # Add files
  git add .

  # Commit
  git commit -m "feat: Initial commit for Desktop Voice-Controlled Assistant"

  # Link to your GitHub repository and push
  git remote add origin https://github.com/<your-username>/<your-repo-name>.git
  git branch -M main
  git push -u origin main
  ```

---

## 📄 License
This project is licensed under the MIT License.
