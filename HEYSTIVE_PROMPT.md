# 🎤 Heystive - Voice Desktop Assistant (Prompt for Gemini Code Assistant)

Build **Heystive**, a local, voice-first desktop assistant.

## What Heystive IS:
- A **voice-first assistant**: Users SPEAK to it and it SPEAKS back (not a text chatbot)
- **Local & private**: Runs on user's machine, not a web service
- **Bilingual & natural**: Speaks Persian (Farsi) and English very fluently and naturally
- **Works offline AND online**: Full functionality offline with local models; extended features when online
- **Minimalist UI**: Extremely simple main interface - NOT a complex dashboard

## Core Requirements:

### 1. VOICE INTERACTION (Primary Feature)

**This is NOT a chatbot. This is a voice assistant.**

- Main interaction: User **speaks** → Heystive **listens** → Heystive **speaks back**
- Text is only shown minimally for reference, not for interaction
- Conversation flows naturally like talking to a person

**Voice Technology:**

**Offline Mode (must work without internet):**
- STT (Speech-to-Text): Use `faster-whisper` or `vosk` - both support Persian well
- TTS (Text-to-Speech): Use `piper-tts` or platform-native voices (high quality)
- Must work completely locally with pre-downloaded models

**Online Mode (optional enhancement):**
- STT: Google Cloud Speech-to-Text or similar
- TTS: Google Cloud TTS, Azure Neural Voices, or similar
- Falls back to offline if connection fails

**Voice Quality:**
- Speak VERY naturally - not robotic
- Persian: Near-native pronunciation, natural rhythm and intonation
- English: Clear, conversational, friendly
- Adjust speed, pitch, pauses for natural conversation flow

**Multiple Voice Profiles:**
- Implement at least 3-4 different voices (different timbres/styles)
- Examples: "Calm Female", "Energetic Male", "Neutral Professional", etc.
- User can select in Settings
- Each profile has: voice ID, speed, pitch, expressiveness level

**Mood Detection & Adaptation:**
- Detect user's approximate mood from:
  - Voice: volume, speed, pitch variation, pauses
  - Text: sentiment, emotion words, frustration indicators
- Possible moods: Calm, Stressed, Frustrated, Sad, Excited, Tired
- Adapt response based on mood:
  - Stressed → slower, calmer tone, more supportive
  - Tired → shorter answers, clearer, slower
  - Excited → match energy slightly
- IMPORTANT: Don't make clinical claims - just adapt helpfully
- Must have toggle in Settings to disable this feature

---

### 2. USER INTERFACE (Extreme Minimalism)

**Main Window (Simple & Clean):**

The main screen should have ONLY:

1. **Large Voice Indicator** (center of screen)
   - Animated visual: glowing circle, waveform, or pulsing orb
   - Shows states: Idle, Listening, Speaking, Thinking
   - This is the main focus - make it beautiful and smooth

2. **Minimal Text Display** (small, unobtrusive)
   - Shows transcription of what user said (fades after moment)
   - Shows assistant's current spoken response (for reference only)
   - Supports RTL for Persian, LTR for English
   - This is SECONDARY - voice is primary

3. **Hotkey Hint** (tiny label)
   - Shows: "Ctrl+Alt+Space to talk" or similar

4. **Settings Icon** (small, corner)
   - Gear icon that opens Settings page

**That's ALL on the main screen. No sidebars, no action logs, no command palettes.**

---

**Settings Page (Separate Window):**

All configuration in a dedicated Settings window with tabs/sections:

**Voice Tab:**
- Microphone selection
- Speaker selection
- Voice Profile dropdown (choose from available voices)
- Speaking Speed slider
- Mood Adaptation toggle (on/off)
- STT Mode: Offline / Online / Auto
- TTS Mode: Offline / Online / Auto

**Mode Tab:**
- Operation Mode: Offline / Online / Auto
- Show current connection status

**Language & UI Tab:**
- Default language: Persian / English
- UI direction: Auto / RTL / LTR
- Theme: Light / Dark

**Hotkeys Tab:**
- Global hotkey to activate listening (default: Ctrl+Alt+Space)
- Hotkey to show/hide Heystive window

**Permissions Tab:**
- File operations (read/write/delete) - toggle
- Launch applications - toggle
- Web access - toggle

**Privacy Tab:**
- Enable/disable conversation logging
- Clear conversation history
- Enable/disable mood detection

**Advanced Tab:**
- Show debug logs
- Model selection (if multiple available)
- Voice engine configuration

---

### 3. CAPABILITIES (Real & Useful)

Heystive must actually DO things, not just chat:

**File & Folder Operations:**
- Browse, read, create, edit files
- Organize, rename, move, copy
- Ask confirmation before deleting

**Application Control:**
- Launch apps by name ("Open VS Code", "Open Terminal")
- Open folders in file explorer
- Open files in appropriate editor

**Web Access (Online Mode):**
- Search the web for information
- Open URLs in browser
- Fetch and summarize web pages

**Scripts & Automation:**
- Generate executable scripts (Python, Bash, etc.)
- Present script and ask before running
- Save scripts to files

**System Information:**
- Show CPU, RAM, disk usage
- List running processes
- Suggest optimizations

**Local Knowledge Base:**
- Maintain local folder (`knowledge/`) with notes, docs
- Store and retrieve information
- Search using keywords or vector search (RAG)
- Works offline

---

### 4. OFFLINE vs ONLINE MODES

**Offline Mode (No Internet Required):**

Must work fully offline with:
- Local STT (faster-whisper or vosk)
- Local TTS (piper-tts or system voices)
- File operations
- App launching
- Local knowledge search
- Script generation and execution

When internet-requiring feature is requested:
- Say: "I need internet for that - currently in offline mode"
- Offer local alternatives if possible

**Online Mode:**

Additional capabilities:
- Cloud STT/TTS (better quality)
- Web search
- Web browsing and summarization
- External APIs (weather, etc.)

**Auto Mode:**
- Detect internet connection
- Use online when available, gracefully fallback to offline

---

### 5. CONVERSATION BEHAVIOR

**Natural Conversation Flow:**
- Keep responses SHORT and conversational (not essays)
- Use natural filler words (Persian: "خب", "ببین", "یعنی" / English: "well", "so", "let me see")
- For technical details: give SHORT spoken summary, then ask "Do you want details?"
- If user interrupts while speaking, stop and listen

**Language:**
- Default to Persian for Persian users
- Seamlessly switch to English when needed
- Detect language from user's speech

**Error Handling:**
- If something fails, explain honestly
- Suggest fixes or alternatives
- Never claim an action was done if it failed

---

### 6. IMPLEMENTATION REQUIREMENTS

**Tech Stack (Suggested):**
- **Python** for backend (easy AI/ML integration)
- **PyQt6** or **Tkinter** for desktop UI (PyQt6 better for RTL and animations)
- **faster-whisper** for offline STT (supports Persian well)
- **piper-tts** for offline TTS (fast, high quality)
- **pynput** for global hotkeys
- **psutil** for system info
- **chromadb** or **faiss** for local knowledge (optional but recommended)

**Project Structure:**
```
heystive/
├── main.py                 # Entry point
├── ui/
│   ├── main_window.py      # Minimalist main screen
│   └── settings_window.py  # Settings page
├── voice/
│   ├── stt.py              # Speech-to-text (offline+online)
│   ├── tts.py              # Text-to-speech (offline+online)
│   └── mood_detector.py    # Mood detection
├── agent/
│   ├── brain.py            # Core logic
│   └── memory.py           # Local knowledge
├── tools/
│   ├── file_tools.py
│   ├── app_tools.py
│   ├── web_tools.py
│   └── system_tools.py
├── config/
│   └── settings.json
└── knowledge/              # Local knowledge base
```

**Development Steps:**
1. Create project structure and basic UI shell
2. Implement offline voice pipeline (STT + TTS) with hotkey
3. Test basic voice conversation loop
4. Add online voice as optional enhancement
5. Implement mood detection (basic version)
6. Wire core tools (files, apps, system)
7. Build settings page with all options
8. Add local knowledge system
9. Polish UI animations and RTL support
10. Test thoroughly in offline and online modes

**Testing Scenarios:**

Test offline mode:
- Disconnect internet
- Press hotkey
- Say (Persian): "یه فایل جدید به اسم test بساز" (Create a new file called test)
- Verify: Voice works, file created, natural Persian response

Test online mode:
- Say: "چطوری پایتون رو آپدیت کنم؟" (How do I update Python?)
- Verify: Web search works, results spoken naturally

Test mood adaptation:
- Speak in stressed tone: "کارها تموم نمی‌شن، خیلی استرس دارم!"
- Verify: Assistant responds slower, calmer, more supportive

---

### 7. KEY PRINCIPLES

1. **Voice-first**: This is NOT a chatbot - it's a voice assistant
2. **Minimal UI**: Main screen is just voice indicator + minimal text
3. **Natural speech**: Fluent, native-like Persian and English
4. **Offline-capable**: Core features work without internet
5. **Mood-aware**: Adapts to user's emotional state (with toggle)
6. **Real capabilities**: Actually does useful things
7. **Clean code**: Modular, extensible architecture

---

## Your Task:

Implement Heystive step-by-step according to this specification.

Start by:
1. Setting up the project structure
2. Creating the minimal UI (main window + settings window)
3. Implementing the offline voice pipeline
4. Testing basic voice interaction
5. Adding capabilities incrementally

Make it REAL and USABLE, not a demo.
