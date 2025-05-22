# AI Voice Chat WebSocket Service

A real-time conversational service that processes text through LLM and converts responses to speech.

## 🛠️ Installation

1. Clone repo and enter directory:
```bash
git clone https://github.com/marco0913/AIVoiceChat.git
cd AIVoiceChat
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your OpenAI API key:
```env
OPENAI_API_KEY=your_key_here
```

## 🚀 Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload
```

Access the web interface at:  
👉 [http://localhost:8000](http://localhost:8000)

## 🧪 Testing

| Test Type | Command |
|-----------|---------|
| Unit Tests | `pytest tests/ -v` |
| Integration Tests | `pytest tests/ -m integration` |
| With Coverage | `pytest --cov=app tests/` |

## ⚙️ Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `OPENAI_LLM_MODEL` | No | `gpt-3.5-turbo` | Chat model |
| `OPENAI_TTS_MODEL` | No | `tts-1` | TTS model |
| `OPENAI_TTS_VOICE` | No | `fable` | Voice style |

