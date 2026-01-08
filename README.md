
Scribe is an experimental AI-powered assistant designed to **organize messy brainstorming notes**, **identify questions and assumptions**, and **verify information when needed**. It helps turn raw ideas into a **clean and structured output**.

This project exists in two forms:

- **Scribe (Local Agent)** – works with text files
- **ScribeBot (Telegram Bot)** – works via chat (text)

> ⚠️ This project was built primarily for **learning and experimentation**. It is not production-ready and intentionally kept simple so it can be improved, extended, or rewritten.

---

## Features

- Organizes raw brainstorm notes into clear ideas
- Detects:
  - Assumptions (explicit & implicit)
  - Questions (explicit & implied)
- Verifies assumptions and answers questions using online tools **only when needed**
- Produces structured output:
  - Ideas
  - Assumptions
  - Assumption checks
  - Verified answers
  - Resources
  - Summary
  - Recommendations
- Telegram bot support
  - Text messages
- Strict JSON-based agent output (easy to parse & extend)

---

## How It Works (High Level)

1. User provides brainstorming content
   - Local agent: text file
   - Telegram bot: text message
2. The agent:
   - Analyzes and organizes the content
   - Identifies ideas, assumptions, and questions
   - Uses search tools **only if external verification is required**
3. The agent returns a **single structured JSON response**
4. The result is converted into a clean, human-readable message

---

## Project Variants

### Scribe (Local Agent)

**What is it?**

Scribe is a local AI agent that helps you organize ideas, find answers, and verify assumptions.

**How it works**

- You brainstorm a topic in a text file
- You provide the file path to the agent
- The agent analyzes the content, organizes ideas, identifies questions and assumptions
- It searches the internet when verification is required
- You receive a clean, well-organized output file

---

### ScribeBot (Telegram Bot)

**What is it?**

ScribeBot is a Telegram-based version of the agent that works through chat.

**How it works**

- You write or paste your brainstorming notes
- The bot analyzes the content
- It organizes ideas, verifies assumptions, answers questions, and adds resources
- The bot replies with a structured, readable message

> ⚠️ This bot is a **demo** and still needs a lot of work. You are encouraged to improve it or build your own version.

## Installation

### Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\\Scripts\\activate     # Windows
```

---

### Install Dependencies

#### Main Libraries

```bash
pip install phidata groq python-dotenv python-telegram-bot
```

#### Tooling Libraries

```bash
pip install duckduckgo-search googlesearch-python pycountry wikipedia
```

---

## Required Accounts & Keys

### Groq (LLM Provider)

- Create a free account
- Generate an API key

[https://console.groq.com/keys](https://console.groq.com/keys)

### Telegram Bot Token

- Create a bot using **@BotFather** on Telegram
- Make sure it is the **official verified BotFather** (blue check mark)
- Copy the bot token

---

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

---

## Running the Bot

```bash
python ScribBot.py
```

Once running, send messages (text or voice) to your Telegram bot.

---

## Architecture (Simplified)

- Telegram Handler
- Input normalization (text)
- Prompt builder
- AI Agent (Groq + PhiData)
- Tool usage (search only when required)
- Strict JSON response
- Markdown formatter
- Telegram response

---

## Known Limitations

- LLM may occasionally return invalid JSON
- Telegram Markdown parsing is fragile
- Error handling is minimal
- Not optimized for large inputs
- Not production-ready

These limitations are **intentional learning points**.

---

## Purpose of This Project

This project was built for **learning by doing**:

- Understanding agent-based architectures
- Prompt design for structured outputs
- Tool-augmented LLMs
- Telegram bot development
- Defensive parsing and error handling

Mistakes are expected — that is part of the process


---

## Ideas for Improvement

- Better JSON validation & retry logic
- Streaming responses
- Web UI
- Database-backed history
- Multi-agent setup
- More robust Markdown escaping

