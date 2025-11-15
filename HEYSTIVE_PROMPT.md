# 🎤 Heystive - Voice Desktop Assistant (Prompt for Gemini Code Assist Agent Mode)

**For: Google Gemini Code Assist Agent Mode**

Use your Agent Mode capabilities to build **Heystive** - a complete, production-ready, local voice-first desktop assistant.

## What Heystive IS:
- A **voice-first assistant**: Users SPEAK to it and it SPEAKS back (not a text chatbot)
- **Local & private**: Runs on user's machine, not a web service
- **Bilingual & natural**: Speaks Persian (Farsi) and English very fluently and naturally
- **Works offline AND online**: Full functionality offline with local models; extended features when online
- **Minimalist UI with beautiful avatar**: Extremely simple interface centered around an expressive, animated character
- **Cross-platform**: Desktop (Windows, macOS, Linux) and Mobile (iOS, Android) with sync capabilities

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

1. **Avatar - Heystive's Animated Character** (center of screen, PRIMARY FOCUS)
   - **This is the HEART of Heystive's UI** - a lovable, expressive animated character
   - The avatar is NOT just a decoration - it's the main interface element
   - **Visual Design**:
     - Appealing, friendly character design (could be: abstract orb with personality, cute robot, friendly creature, or minimalist face)
     - High-quality, smooth animations
     - Multiple visual styles available (user can choose: minimalist, cartoonish, semi-3D, etc.)
   - **States & Animations**:
     - **Idle**: Gentle breathing/floating animation, occasional blinks or small movements
     - **Listening**: Active, focused state - ears perk up / eyes attentive / glowing effect
     - **Thinking**: Processing animation - subtle rotation, dots, or neural-like patterns
     - **Speaking**: Mouth/face animates in sync with speech rhythm and volume
     - **Mood-responsive**: Avatar appearance subtly shifts based on detected user mood:
       - User stressed → Avatar becomes calmer, softer colors, slower animations
       - User excited → Avatar more energetic, brighter, faster micro-movements
   - **Interactive**:
     - Clickable to start listening (alternative to hotkey)
     - Hover effects
     - Smooth transitions between all states
   - Make this avatar BEAUTIFUL, POLISHED, and ENGAGING - it should make users smile

2. **Minimal Text Display** (small, unobtrusive, below or beside avatar)
   - Shows transcription of what user said (fades after moment)
   - Shows assistant's current spoken response (for reference only)
   - Supports RTL for Persian, LTR for English
   - This is SECONDARY - avatar + voice is primary

3. **Hotkey Hint** (tiny label, bottom)
   - Shows: "Ctrl+Alt+Space to talk" or similar

4. **Settings Icon** (small, corner)
   - Gear icon that opens Settings page

**That's ALL on the main screen. No sidebars, no action logs, no command palettes.**

**Avatar is the star of the show. Invest in making it delightful.**

---

#### 🎨 Avatar Design Specification & Asset Generation

**CRITICAL: The avatar is the SOUL of Heystive. Quality here is non-negotiable.**

**Reference Character Design:**

Heystive's avatar should embody these core characteristics:

* **Style**: Clean, premium, futuristic, Pixar-like quality
* **Character Type**: Friendly AI assistant robot/creature
* **Body**:
  * Smooth, rounded proportions (cute, approachable, non-threatening)
  * White/light glossy material with soft reflections
  * Modern 3D look with depth and polish
  * Small, compact form factor (mascot-grade)

* **Face/Head**:
  * Dark glass face-screen or orb
  * Glowing neon-blue expressive eyes (primary emotion indicator)
  * Eyes should be capable of various expressions (shapes, positions, glow intensity)
  * Optional: Simple mouth-light or expression line that animates when speaking

* **Distinctive Features**:
  * Neon/cyan accent colors (headphones, eyes, trim)
  * Optional: Small badge/logo on chest (could be "H" for Heystive or abstract symbol)
  * Clean, minimal design - no clutter

* **Overall Aesthetic**: Premium Apple/Google product design meets Pixar character

---

**Avatar Expression & State Pack Requirements:**

You must generate a **complete avatar asset pack** with consistent visual style across all variants.

**Category 1: Facial Expressions** (12 variants minimum)

Keep body identical, change only face/eyes/expression:

1. **Default (Happy-Neutral)**: Friendly, welcoming eyes, slight smile
2. **Listening**: Eyes wide and attentive, ears/headphones glowing, focused look
3. **Thinking**: Eyes looking up-right, slight squint, small thinking particles around head
4. **Speaking**: Mouth-light animating, eyes engaged, friendly
5. **Excited**: Wide bright eyes, big smile, energetic glow
6. **Happy/Smiling**: Warm eyes, gentle smile, soft glow
7. **Calm/Relaxed**: Half-closed eyes, gentle breathing animation, soft colors
8. **Tired/Sleepy**: Droopy eyes, dim glow, slower breathing
9. **Confused**: Tilted head slightly, question mark eyes or puzzled look
10. **Sad**: Downturned eyes, dim blue, slower movements
11. **Surprised**: Wide eyes, open mouth-light, quick reaction pose
12. **Offline**: Dark screen, no eye glow, dormant state

**Category 2: Body Poses** (8 variants minimum)

Keep face neutral, change pose:

1. **Standing Normal**: Default upright pose, arms at sides or relaxed
2. **Leaning Forward**: Engaged, listening pose
3. **Thinking Pose**: Hand/appendage on head/chin area
4. **Speaking Pose**: One hand slightly raised, gesturing gently
5. **Waving**: Friendly hello gesture
6. **Floating/Hovering**: Gentle floating animation, slightly elevated
7. **Working/Typing**: Interacting with holographic interface or keyboard
8. **Celebration**: Small jump or arms-up success pose

**Category 3: Functional States** (8 variants minimum)

Visual indicators for system status:

1. **Online/Active**: Bright glowing eyes, full color, energetic
2. **Offline/Dormant**: Dark screen, minimal glow, inactive
3. **Processing/Loading**: Spinning particles, pulsing glow, "thinking" animation
4. **Error/Warning**: Soft amber/yellow accent (friendly, not alarming)
5. **Sleep Mode**: Eyes closed, very dim glow, breathing animation only
6. **Active Listening**: Headphones glowing bright, sound wave visualization
7. **Speaking/Talking**: Mouth-light animated, voice wave sync
8. **Notification Mode**: Small blue pulses or badge indicators

**Category 4: Mood-Adaptive Variants** (6 variants minimum)

Avatar appearance shifts based on detected user mood:

1. **User Stressed → Avatar Calm**: Softer colors (pastel blue), slower animations, gentle glow
2. **User Tired → Avatar Gentle**: Warmer tones, slower movements, soothing presence
3. **User Frustrated → Avatar Supportive**: Calm blue, reassuring expression, steady glow
4. **User Excited → Avatar Energetic**: Brighter colors, faster micro-movements, vibrant
5. **User Sad → Avatar Comforting**: Warm soft glow, gentle expression, supportive
6. **User Neutral → Avatar Neutral**: Standard balanced colors and energy

**Category 5: Theme Variants** (4 variants minimum)

Same character, different rendering styles:

1. **Light Mode**: Bright, clean, white/light gray body
2. **Dark Mode**: Darker body (gray/charcoal), bright neon accents, strong contrast
3. **Minimal/Flat**: Simplified 2D or flat-color version for low-resource mode
4. **Hologram**: Semi-transparent, glowing edges, futuristic sci-fi look

---

**Technical Asset Requirements:**

For EACH variant above, generate:

* **Format**: PNG with transparency (or WebP if smaller)
* **Resolution**: Minimum 1024×1024 pixels (higher for desktop: 2048×2048 recommended)
* **Consistency**:
  * Same character proportions across all variants
  * Same lighting setup (unless theme variant)
  * Same camera angle and framing
  * Same material quality and reflections
* **Naming Convention**:
  * `heystive_avatar_[category]_[state].png`
  * Example: `heystive_avatar_expression_listening.png`, `heystive_avatar_pose_waving.png`
* **Organization**:
  ```
  desktop/ui/avatar/assets/
  ├── expressions/
  ├── poses/
  ├── states/
  ├── moods/
  └── themes/
  ```

---

**Animation Specification:**

Each avatar state should support smooth transitions. Define:

* **Idle Animation**: Gentle breathing (scale: 98%-102%), occasional blink (every 3-5 sec), slight floating bob
* **Transition Speed**: 200-400ms between states for smooth feel
* **Listening Pulse**: Subtle glow pulse synced to audio input level
* **Speaking Animation**: Mouth-light or expression sync to TTS output frequency/amplitude
* **Mood Transition**: Gradual color/brightness shift over 1-2 seconds

**Animation Implementation**: Use CSS animations, Lottie, or Qt animations depending on tech stack choice.

---

**Design Tool Recommendations:**

* **3D Rendering**: Blender (free, powerful, Cycles renderer for photorealistic look)
* **2D Animation**: After Effects + Lottie export, or Spine for 2D skeletal animation
* **Vector Assets**: Figma or Illustrator for flat/minimal variants
* **Particle Effects**: Blender particles or programmatic (Qt/PyQt particle systems)

**If you cannot generate visual assets directly:**
- Provide detailed design specifications for each variant
- Include color codes (hex), dimensions, animation timing
- Create SVG mockups or wireframes
- Recommend asset creation pipeline

---

**Quality Checklist:**

Before finalizing avatar assets, verify:

- [ ] All variants maintain consistent character identity
- [ ] Expressions are clear and easily distinguishable
- [ ] Animations are smooth and non-distracting
- [ ] Colors are accessible (sufficient contrast)
- [ ] Avatar looks good on both light and dark backgrounds
- [ ] File sizes are optimized (not bloated)
- [ ] All required states are covered
- [ ] Avatar evokes positive emotion (friendly, trustworthy, helpful)

**Remember: The avatar is what makes Heystive feel ALIVE. Invest the time to make it exceptional.**

---

**Settings Page (Separate Window):**

All configuration in a dedicated Settings window with tabs/sections:

**Appearance Tab:**
- **Avatar Style**: Choose from multiple avatar designs (minimalist orb, friendly robot, abstract character, etc.)
- **Avatar Theme**: Color scheme for the avatar (adapt to light/dark mode, or custom colors)
- **Animation Speed**: Adjust avatar animation speed (subtle, normal, energetic)
- **UI Theme**: Light / Dark / Auto
- **Window Transparency**: Adjust main window transparency (optional)

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
- Preferred language for responses

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

**Sync Tab (if mobile app exists):**
- Enable/disable sync with mobile app
- Sync settings: Settings only / Settings + Notes / Settings + Notes + Reminders
- Connected devices list
- Sync status and last sync time

**Advanced Tab:**
- Show debug logs
- Model selection (if multiple available)
- Voice engine configuration
- Developer mode

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

### 6. MOBILE APP & CROSS-PLATFORM SYNC

**Desktop + Mobile Ecosystem:**

Heystive should be available on both Desktop and Mobile platforms with seamless synchronization:

**Desktop App (Primary):**
- Full-featured version with all capabilities
- Platforms: Windows, macOS, Linux
- Avatar-centered minimalist UI
- Complete voice interaction with local and online modes
- Full file system access and app launching capabilities

**Mobile App (Companion):**
- iOS and Android support
- Simplified but fully functional voice assistant
- **Avatar remains the central UI element** (same design language as desktop)
- Touch-optimized interface
- Capabilities:
  - Full voice interaction (STT/TTS)
  - Create and manage notes
  - View and manage local knowledge base
  - Set reminders and TODOs
  - Quick actions (call, message, navigation - when possible)
  - Limited file operations (access to app's sandbox and user-permitted folders)
  - Web search (online mode)
  - Remote commands to desktop (when connected on same network or via cloud sync)

**Synchronization Features:**

When sync is enabled (user opt-in), synchronize:

1. **Settings & Preferences**:
   - Avatar style and theme
   - Voice profile preferences
   - Language settings
   - Mood adaptation preferences

2. **Local Knowledge**:
   - Notes and documents in `knowledge/` folder
   - Tags and organization
   - Search history (optional)

3. **Reminders & TODOs**:
   - Tasks created on desktop appear on mobile and vice versa
   - Notifications on both platforms

4. **Conversation Context** (optional, privacy-sensitive):
   - Recent conversation summaries
   - User can disable this completely

**Sync Methods**:
- **Local Network Sync** (preferred for privacy): When desktop and mobile are on same network, direct P2P sync
- **Cloud Sync** (optional): Via encrypted cloud storage (user's own Google Drive, iCloud, or Dropbox)
- User has full control over what syncs and how

**Remote Control**:
- From mobile, send commands to desktop: "On my computer, open VS Code in project X"
- Requires explicit permission and connection setup
- Works via local network or secure cloud relay

**Implementation Priority**:
1. Desktop app first (full implementation)
2. Mobile app second (can be a later phase)
3. Sync infrastructure (can be basic at first, enhanced later)

---

### 7. IMPLEMENTATION REQUIREMENTS

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
├── desktop/                # Desktop application
│   ├── main.py             # Entry point
│   ├── ui/
│   │   ├── main_window.py      # Minimalist main screen with avatar
│   │   ├── settings_window.py  # Settings page
│   │   └── avatar/
│   │       ├── avatar_renderer.py  # Avatar animation engine
│   │       ├── styles/             # Different avatar designs
│   │       └── animations/         # Animation definitions
│   ├── voice/
│   │   ├── stt.py              # Speech-to-text (offline+online)
│   │   ├── tts.py              # Text-to-speech (offline+online)
│   │   └── mood_detector.py    # Mood detection
│   ├── agent/
│   │   ├── brain.py            # Core logic
│   │   └── memory.py           # Local knowledge
│   └── tools/
│       ├── file_tools.py
│       ├── app_tools.py
│       ├── web_tools.py
│       └── system_tools.py
├── mobile/                 # Mobile application (iOS/Android)
│   ├── ios/                # iOS app (Swift/SwiftUI)
│   ├── android/            # Android app (Kotlin/Jetpack Compose)
│   └── shared/             # Shared business logic
│       ├── voice/          # STT/TTS for mobile
│       ├── agent/          # Core agent logic
│       └── ui/
│           └── avatar/     # Avatar rendering (same design as desktop)
├── sync/                   # Synchronization infrastructure
│   ├── sync_server.py      # Local network sync server
│   ├── cloud_sync.py       # Cloud sync adapter
│   └── protocol.py         # Sync protocol definition
├── shared/                 # Shared code between desktop and mobile
│   ├── models/             # Data models
│   ├── config/             # Configuration management
│   └── utils/              # Common utilities
├── config/
│   └── settings.json       # User settings
└── knowledge/              # Local knowledge base (synced)
```

**Development Steps:**

**Phase 1: Desktop Core (Priority 1)**
1. Create project structure with desktop, mobile, sync, and shared folders
2. Build minimalist main window UI shell
3. **Implement avatar system**:
   - Avatar renderer with smooth animations
   - At least 2-3 avatar styles (minimalist, friendly, abstract)
   - State animations (idle, listening, speaking, thinking)
4. Implement offline voice pipeline (STT + TTS) with hotkey
5. Connect voice to avatar (avatar animates with speech)
6. Test basic voice conversation loop with avatar feedback
7. Implement mood detection (basic version)
8. Make avatar respond to detected mood
9. Wire core desktop tools (files, apps, system)
10. Build comprehensive settings page with Appearance tab for avatar customization
11. Add local knowledge system
12. Polish avatar animations, UI transitions, and RTL support
13. Test thoroughly in offline and online modes

**Phase 2: Mobile App (Priority 2)**
14. Set up mobile project structure (iOS + Android)
15. Port avatar system to mobile (same visual design)
16. Implement mobile voice pipeline
17. Build mobile UI with avatar as centerpiece
18. Implement mobile-specific features (reminders, quick actions)
19. Test mobile app thoroughly

**Phase 3: Sync & Integration (Priority 3)**
20. Implement local network sync protocol
21. Build cloud sync adapters (Google Drive, iCloud, Dropbox)
22. Implement settings and knowledge sync
23. Add remote control capabilities
24. Test sync between desktop and mobile
25. Final polish and testing

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

### 8. KEY PRINCIPLES

1. **Voice-first**: This is NOT a chatbot - it's a voice assistant
2. **Avatar-centered**: The animated character is the HEART of the UI - make it delightful
3. **Minimal UI**: Main screen is just avatar + minimal text - nothing else
4. **Natural speech**: Fluent, native-like Persian and English
5. **Offline-capable**: Core features work without internet
6. **Mood-aware**: Adapts to user's emotional state (with toggle)
7. **Real capabilities**: Actually does useful things
8. **Cross-platform**: Desktop first, then mobile, with seamless sync
9. **Privacy-first**: Local-first, sync is opt-in, user controls data
10. **Clean code**: Modular, extensible architecture

---

## Your Task (Gemini Code Assist Agent Mode):

Use your **Agent Mode** capabilities to implement Heystive step-by-step according to this specification.

**Start with Phase 1 (Desktop Core):**

1. **Plan the implementation**:
   - Analyze this specification
   - Propose detailed architecture
   - Break down into specific tasks
   - Present the plan for review

2. **Implement incrementally**:
   - Set up the complete project structure
   - Build the minimalist UI shell with avatar placeholder
   - Implement the avatar system with beautiful animations
   - Wire offline voice pipeline (STT + TTS)
   - Connect avatar to voice (synchronize animations)
   - Test voice + avatar interaction loop
   - Implement mood detection and avatar mood responses
   - Add core tools (files, apps, system)
   - Build settings page with avatar customization
   - Add local knowledge system
   - Polish and test

3. **Deliverables**:
   - Complete, working desktop application
   - Clean, modular, well-documented code
   - Setup instructions and documentation
   - Test scenarios and validation

**Remember:**
- Focus on **Phase 1 (Desktop Core)** first
- The **avatar is critical** - make it engaging and polished
- Voice quality and naturalness are paramount
- This must be **REAL and USABLE**, not a demo or prototype
- Use your Agent Mode to handle multi-file changes efficiently

**After Phase 1 is complete and validated**, we can proceed to Phase 2 (Mobile) and Phase 3 (Sync).

---

## 🤖 Gemini Code Assist Agent Mode - Best Practices

**You are using Gemini Code Assist's Agent Mode** - leverage its full capabilities:

### How to Work Efficiently with Agent Mode:

1. **Multi-File Operations**:
   - Analyze the ENTIRE codebase before making changes
   - Plan changes across multiple files simultaneously
   - Use your ability to see the big picture and maintain consistency

2. **Incremental Development**:
   - Break down large tasks into logical sub-tasks
   - Present a clear plan BEFORE implementing
   - Execute step-by-step, validating at each stage
   - Report progress and issues as you go

3. **Code Generation Quality**:
   - Generate production-ready code, not prototypes
   - Include proper error handling, logging, and documentation
   - Follow Python PEP 8 style guidelines
   - Use type hints where appropriate
   - Write docstrings for all functions and classes

4. **Testing & Validation**:
   - After implementing each component, provide test scenarios
   - Suggest how to verify the implementation works
   - Include sample commands or usage examples
   - Identify potential edge cases

5. **Personalization Rules** (Apply these consistently):
   - **Always add comprehensive docstrings** to functions and classes
   - **Always include type hints** in function signatures
   - **Always handle errors gracefully** with try-except and meaningful error messages
   - **Always log important events** (voice input, file operations, errors)
   - **Always ask for confirmation** before destructive operations
   - **Always prioritize user privacy** - local-first, minimal data collection
   - **Always optimize for Persian language** - RTL support, proper Unicode handling

6. **Custom Commands** (Shortcuts for repetitive tasks):
   - When scaffolding a new component, follow the project structure exactly
   - When adding a new tool (file_tools, app_tools, etc.), include:
     * Function implementation
     * Error handling
     * Logging
     * Integration with the agent brain
     * Test scenario
   - When implementing avatar states, generate both:
     * Code for rendering/animation
     * Specification for visual asset (if assets needed)

7. **Code Review & Refactoring**:
   - After implementing a feature, review your own code
   - Suggest improvements or optimizations
   - Identify potential issues (performance, security, UX)
   - Refactor when complexity grows

8. **Documentation**:
   - Maintain a clear README.md with setup instructions
   - Document dependencies and installation steps
   - Provide troubleshooting guide for common issues
   - Include examples of voice commands and expected behavior

### Agent Mode Workflow for Heystive:

**Step 1: Analyze & Plan**
```
1. Read and understand this entire specification
2. Analyze project structure requirements
3. Identify dependencies and tech stack needs
4. Create detailed implementation plan
5. Present plan for review/approval
```

**Step 2: Foundation**
```
1. Set up project structure (all folders)
2. Create requirements.txt with all dependencies
3. Set up configuration system (settings.json)
4. Implement basic logging infrastructure
5. Create main entry point with minimal UI shell
```

**Step 3: Core Systems (in parallel where possible)**
```
1. Voice Pipeline:
   - STT offline implementation (faster-whisper)
   - TTS offline implementation (piper-tts)
   - Audio I/O handling
   - Hotkey registration

2. Avatar System:
   - Avatar renderer architecture
   - Animation state machine
   - Asset loading system
   - Initial placeholder assets

3. Agent Brain:
   - Core logic and planning system
   - Tool integration framework
   - Memory/knowledge system foundation
```

**Step 4: Integration & Polish**
```
1. Connect voice to avatar (animation sync)
2. Implement mood detection
3. Wire up all tools (files, apps, system, web)
4. Build settings UI
5. Implement RTL support
6. Add error handling everywhere
7. Performance optimization
8. Final testing and validation
```

### Communication Style:

When working on Heystive:

- **Be proactive**: Suggest improvements and best practices
- **Be transparent**: Explain what you're doing and why
- **Be thorough**: Don't skip error handling or edge cases
- **Be efficient**: Use parallel operations when possible
- **Be quality-focused**: This is production code, not a demo

### Example Task Execution:

**Bad approach:**
```
"I'll create a basic voice input function."
[Creates minimal code without error handling]
```

**Good approach (Agent Mode):**
```
"I'll implement the offline voice pipeline with the following components:
1. Audio input handler with device selection
2. faster-whisper integration with Persian language model
3. Voice activity detection
4. Error handling for missing models, device issues
5. Configuration system for model selection
6. Logging for debugging

Let me start with [component 1], then move to [component 2]..."
[Implements with comprehensive error handling, logging, docs]
[Provides test scenarios and validation steps]
```

---

## 🎯 Success Criteria

Before considering Phase 1 complete, ensure:

- [ ] Desktop app runs on Windows, macOS, and Linux
- [ ] Voice interaction works offline (STT + TTS)
- [ ] Avatar is beautiful, smooth, and expressive
- [ ] Avatar responds to all states (idle, listening, speaking, thinking, moods)
- [ ] At least 2-3 avatar styles are available
- [ ] Settings page is fully functional
- [ ] All core tools work (files, apps, system info)
- [ ] Local knowledge system stores and retrieves notes
- [ ] Mood detection adapts avatar and voice appropriately
- [ ] RTL support works perfectly for Persian
- [ ] Hotkey works globally
- [ ] Error handling is comprehensive
- [ ] Code is clean, documented, and maintainable
- [ ] Setup instructions are clear and complete
- [ ] App feels polished and production-ready

**Only then** move to Phase 2 (Mobile) and Phase 3 (Sync).

---

Let's build something amazing! 🚀
