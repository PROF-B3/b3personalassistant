# 🔌 Integration Setup Guide

Complete guide to setting up and using all B3PersonalAssistant integrations.

## 📋 Table of Contents

1. [Web API Setup](#web-api-setup)
2. [Gmail Integration](#gmail-integration)
3. [Google Calendar Integration](#google-calendar-integration)
4. [Voice Interface](#voice-interface)
5. [Troubleshooting](#troubleshooting)

---

## 1. Web API Setup 🌐

The FastAPI web interface provides REST API and WebSocket access to all features.

### Installation

```bash
# Install with integrations support
pip install -e ".[integrations]"
```

### Running the Server

```bash
# Navigate to web API directory
cd interfaces/web_api

# Run the server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws

### API Examples

**Get Context:**
```bash
curl -X POST "http://localhost:8000/api/context/get" \
  -H "Content-Type: application/json" \
  -d '{"key": "current_task", "context_type": "conversation"}'
```

**Semantic Search:**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "how to improve productivity", "top_k": 5}'
```

**Get Suggestions:**
```bash
curl "http://localhost:8000/api/proactive/suggestions?limit=5"
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({ type: 'subscribe' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

---

## 2. Gmail Integration 📧

Access and manage Gmail through the assistant.

### Prerequisites

1. **Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API

2. **OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Create "OAuth 2.0 Client ID"
   - Application type: "Desktop app"
   - Download `credentials.json`

### Setup

```bash
# Install dependencies
pip install -e ".[integrations]"

# Place credentials.json in project root
cp ~/Downloads/credentials.json ./credentials.json

# Set environment variables (optional)
export GMAIL_CREDENTIALS_PATH="./credentials.json"
export GMAIL_TOKEN_PATH="./gmail_token.pickle"
```

### First-Time Authentication

```python
from modules.integrations.gmail_integration import GmailIntegration

# Initialize
gmail = GmailIntegration()

# Authenticate (opens browser for OAuth)
if gmail.authenticate():
    print("✅ Authenticated!")
else:
    print("❌ Authentication failed")
```

**Important**: The first authentication will:
1. Open your browser
2. Ask you to sign in to Google
3. Request permissions
4. Save `token.pickle` for future use

### Usage Examples

**Read Unread Emails:**
```python
# Get last 10 unread emails
emails = gmail.get_emails(unread_only=True, max_results=10)

for email in emails:
    print(f"From: {email.sender}")
    print(f"Subject: {email.subject}")
    print(f"Date: {email.date}")
    print(f"---")
```

**Send Email:**
```python
message_id = gmail.send_email(
    to="recipient@example.com",
    subject="Hello from B3Assistant",
    body="This email was sent programmatically!"
)

if message_id:
    print(f"✅ Email sent: {message_id}")
```

**Search Emails:**
```python
# Search with Gmail query syntax
emails = gmail.get_emails(
    query="from:boss@company.com subject:urgent",
    max_results=5
)
```

**Mark as Read/Unread:**
```python
gmail.mark_as_read(email_id)
gmail.mark_as_unread(email_id)
```

**Get Email Summary:**
```python
emails = gmail.get_emails(unread_only=True)
summary = gmail.summarize_emails(emails)

print(f"Total: {summary['total']}")
print(f"High priority: {summary['high_priority']}")
print(f"Top senders: {summary['senders']}")
```

**Extract Action Items:**
```python
email = emails[0]
actions = gmail.extract_action_items(email)

for action in actions:
    print(f"TODO: {action}")
```

### Integration with Workflows

```python
from modules.workflow_engine import *

# Create email monitoring workflow
workflow = Workflow(
    name="High Priority Email Alert",
    trigger=Trigger(
        trigger_type="event_based",
        config={"event": "email_received", "filter": {"importance": "high"}},
        description="When high-priority email arrives"
    ),
    actions=[
        Action(
            action_type="send_notification",
            config={"title": "High Priority Email!", "message": "{subject}"},
            description="Alert user"
        ),
        Action(
            action_type="create_task",
            config={"title": "Respond to {sender}", "priority": "high"},
            description="Create task"
        )
    ]
)
```

---

## 3. Google Calendar Integration 📅

Manage calendar events and find free time.

### Prerequisites

**Same as Gmail:**
1. Google Cloud Project with Calendar API enabled
2. OAuth credentials (`credentials.json`)

### Setup

```bash
# Use same credentials.json as Gmail
# Or use separate credentials if you prefer
export CALENDAR_CREDENTIALS_PATH="./credentials.json"
export CALENDAR_TOKEN_PATH="./calendar_token.pickle"
```

### Authentication

```python
from modules.integrations.calendar_integration import CalendarIntegration

calendar = CalendarIntegration()

if calendar.authenticate():
    print("✅ Calendar authenticated!")
```

### Usage Examples

**Get Today's Events:**
```python
from datetime import datetime, timedelta

today = datetime.now().replace(hour=0, minute=0, second=0)
tomorrow = today + timedelta(days=1)

events = calendar.get_events(today, tomorrow)

for event in events:
    print(f"{event.start.strftime('%H:%M')} - {event.summary}")
```

**Create Event:**
```python
from datetime import datetime, timedelta

# Schedule meeting for tomorrow at 2 PM
start = datetime.now().replace(hour=14, minute=0) + timedelta(days=1)

event_id = calendar.create_event(
    summary="Team Meeting",
    start=start,
    duration_minutes=60,
    location="Conference Room A",
    attendees=["team@company.com"],
    reminders=[10, 5]  # 10 and 5 minutes before
)
```

**Find Free Time Slots:**
```python
# Find 1-hour slots tomorrow
tomorrow = datetime.now() + timedelta(days=1)
start = tomorrow.replace(hour=9, minute=0)
end = tomorrow.replace(hour=17, minute=0)

free_slots = calendar.find_free_slots(start, end, duration_minutes=60)

for slot in free_slots:
    print(f"{slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}")
```

**Check for Conflicts:**
```python
# Check if proposed time conflicts with existing events
proposed_start = datetime(2024, 1, 15, 14, 0)
proposed_end = datetime(2024, 1, 15, 15, 0)

conflicts = calendar.check_conflicts(proposed_start, proposed_end)

if conflicts:
    print(f"⚠️  Conflicts with {len(conflicts)} events:")
    for event in conflicts:
        print(f"  - {event.summary}")
else:
    print("✅ No conflicts!")
```

**Daily Summary:**
```python
summary = calendar.get_daily_summary()

print(f"📅 {summary['date']}")
print(f"Total events: {summary['total_events']}")
print(f"Total time: {summary['total_duration_minutes']} minutes")
print(f"First: {summary['first_event']}")
print(f"Last: {summary['last_event']}")
```

### Smart Scheduling

Combine with Proactive Agent for intelligent scheduling:

```python
from modules.agents.proactive_agent import ProactiveAgent

proactive = ProactiveAgent()

# Record meeting patterns
proactive.record_action("attended_standup", context="morning")
proactive.record_action("review_meeting", context="friday_afternoon")

# Get free slots
free_slots = calendar.find_free_slots(...)

# Filter based on patterns
# Suggest best times based on learned preferences
```

---

## 4. Voice Interface 🎤🔊

Speech-to-text and text-to-speech capabilities.

### Installation

```bash
# Install voice dependencies
pip install -e ".[voice,multimodal]"

# Install system dependencies

# For macOS:
brew install portaudio
brew install ffmpeg

# For Ubuntu/Debian:
sudo apt-get install portaudio19-dev python3-pyaudio
sudo apt-get install ffmpeg

# For Windows:
# Download and install PyAudio wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

### Usage Examples

**Listen and Transcribe:**
```python
from modules.voice_interface import VoiceInterface

voice = VoiceInterface()

# Listen for 5 seconds
print("Speak now...")
text = voice.listen(duration=5)

if text:
    print(f"You said: {text}")
```

**Text-to-Speech:**
```python
# Speak text
voice.speak("Hello! How can I help you today?")

# Save to file
voice.speak("This will be saved", save_to_file="output.mp3")
```

**Transcribe Audio File:**
```python
# Transcribe meeting recording
text = voice.transcribe_file("meeting_recording.mp3")
print(text)

# Index in semantic search
from modules.semantic_search import SemanticSearchEngine

search = SemanticSearchEngine()
search.index_text(text, "meeting", "meeting_2024_01_15")
```

**Voice Commands:**
```python
commands = [
    "open email",
    "check calendar",
    "create task",
    "search notes"
]

print("Say a command...")
text = voice.listen()

if text:
    command = voice.recognize_command(text, commands)
    if command:
        print(f"Executing: {command}")
        # Execute command...
```

**Continuous Listening:**
```python
def handle_command(text):
    print(f"Processing: {text}")
    # Process command...
    voice.speak(f"Executing: {text}")

# Listen continuously until Ctrl+C
voice.continuous_listen(handle_command, commands=["email", "calendar", "tasks"])
```

### Voice Activity Detection

```python
# Detect when speech occurs in audio file
segments = voice.detect_voice_activity("recording.wav")

for start, end in segments:
    print(f"Speech: {start:.2f}s - {end:.2f}s")
    duration = end - start
    print(f"Duration: {duration:.2f}s")
```

---

## 5. Troubleshooting 🔧

### Gmail/Calendar Authentication Issues

**Problem**: "credentials.json not found"
```bash
# Solution: Ensure credentials.json is in the right location
export GMAIL_CREDENTIALS_PATH="/path/to/credentials.json"
```

**Problem**: "Access blocked: This app's request is invalid"
```bash
# Solution:
# 1. Go to Google Cloud Console
# 2. OAuth consent screen → Edit app
# 3. Add your email as test user
# 4. Save and try again
```

**Problem**: "Token has been expired or revoked"
```bash
# Solution: Delete token and re-authenticate
rm token.pickle
rm calendar_token.pickle
# Run authentication again
```

### Voice Interface Issues

**Problem**: "PyAudio not found"
```bash
# macOS
brew install portaudio
pip install pyaudio

# Ubuntu
sudo apt-get install portaudio19-dev
pip install pyaudio

# Windows
# Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl
```

**Problem**: "No microphone detected"
```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Specify microphone index
import speech_recognition as sr
with sr.Microphone(device_index=1) as source:
    # Use specific microphone
```

**Problem**: "Whisper model download fails"
```bash
# Manually download models
import whisper
whisper.load_model("base")  # Downloads model
```

### Web API Issues

**Problem**: "Connection refused on port 8000"
```bash
# Check if port is in use
lsof -i :8000

# Use different port
uvicorn main:app --port 8080
```

**Problem**: "CORS errors in browser"
```python
# Update CORS settings in main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### General Debugging

**Enable debug logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check dependencies:**
```bash
pip list | grep -i google
pip list | grep -i speech
pip list | grep -i whisper
```

**Test individual components:**
```python
# Test Gmail
from modules.integrations.gmail_integration import GmailIntegration
gmail = GmailIntegration()
print(gmail.dependencies_available)

# Test Calendar
from modules.integrations.calendar_integration import CalendarIntegration
calendar = CalendarIntegration()
print(calendar.dependencies_available)

# Test Voice
from modules.voice_interface import VoiceInterface
voice = VoiceInterface()
print(voice.available_engines)
```

---

## Quick Reference

### Environment Variables

```bash
# Gmail
export GMAIL_CREDENTIALS_PATH="./credentials.json"
export GMAIL_TOKEN_PATH="./gmail_token.pickle"

# Calendar
export CALENDAR_CREDENTIALS_PATH="./credentials.json"
export CALENDAR_TOKEN_PATH="./calendar_token.pickle"

# Web API
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

### Installation Commands

```bash
# All features
pip install -e ".[full,multimodal,integrations,voice]"

# Just integrations
pip install -e ".[integrations]"

# Just voice
pip install -e ".[voice,multimodal]"
```

### Testing Integrations

```bash
# Test Gmail
python -c "from modules.integrations.gmail_integration import GmailIntegration; g = GmailIntegration(); print('✅' if g.authenticate() else '❌')"

# Test Calendar
python -c "from modules.integrations.calendar_integration import CalendarIntegration; c = CalendarIntegration(); print('✅' if c.authenticate() else '❌')"

# Test Voice
python -c "from modules.voice_interface import VoiceInterface; v = VoiceInterface(); print('✅ Voice ready')"

# Test Web API
curl http://localhost:8000/health
```

---

## Next Steps

1. **Set up Gmail and Calendar** following the authentication steps
2. **Start the web server** to access the API and web interface
3. **Try voice commands** for hands-free interaction
4. **Create workflows** that automate email and calendar tasks
5. **Integrate everything** with the proactive agent for intelligent automation

For more examples, see [FEATURES.md](FEATURES.md)
