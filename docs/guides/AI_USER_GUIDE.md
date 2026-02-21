# AI Features User Guide

This guide explains how to use the AI features in Veryfyn.

## Table of Contents

1. [Getting Started](#getting-started)
2. [AI Assistant](#ai-assistant)
3. [Digital Coach](#digital-coach)
4. [Weekly Summaries](#weekly-summaries)
5. [Provider Setup](#provider-setup)
6. [API Key Management](#api-key-management)
7. [Privacy & Security](#privacy--security)

---

## Getting Started

### First-Time Setup

When you first access AI features, you'll be guided through a setup wizard:

1. **Choose a Provider**: Select your AI provider (Ollama for local, or cloud providers)
2. **Configure API Key**: If using a cloud provider, enter your API key
3. **Select Model**: Choose the AI model to use
4. **Enable Features**: Choose which AI features to enable

### Quick Start with Ollama (Free, Local)

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Run in terminal: `ollama serve`
3. Pull a model: `ollama pull llama3`
4. Open Veryfyn and select "Ollama" as your provider

### Quick Start with Cloud Providers

1. Get an API key from your chosen provider:
   - [OpenAI](https://platform.openai.com/api-keys)
   - [Anthropic](https://console.anthropic.com/settings/keys)
   - [Google Gemini](https://makersuite.google.com/app/apikey)
   - [Groq](https://console.groq.com/keys)
2. Open Veryfyn AI Settings
3. Select your provider and enter the API key

---

## AI Assistant

The AI Assistant is a chat interface that lets you interact with your tracking data.

### Features

- **Ask Questions**: "How am I doing with my habits?"
- **Get Insights**: "What patterns do you see in my sleep?"
- **Set Goals**: "Help me create a fitness goal"
- **Track Progress**: "What's my task completion rate this week?"

### Usage Tips

1. **Be Specific**: The more specific your question, the better the answer
2. **Use Context**: Reference specific habits, tasks, or time periods
3. **Follow Up**: Ask follow-up questions to dive deeper

### Example Queries

```
"What habits am I struggling with?"
"How many tasks did I complete last week?"
"What's my longest current streak?"
"Give me a summary of my goals"
"How does my sleep affect my mood?"
```

---

## Digital Coach

The Digital Coach provides proactive guidance and interventions based on your tracking data.

### How It Works

1. **Monitors Your Data**: Continuously analyzes your habits, tasks, goals, and health
2. **Detects Patterns**: Identifies trends, risks, and opportunities
3. **Provides Interventions**: Offers timely suggestions and encouragement
4. **Adapts to You**: Adjusts intensity based on your current state

### Intervention Types

| Type | Trigger | Example |
|------|---------|---------|
| **Burnout Warning** | High stress indicators | "You've been working hard. Consider taking a break." |
| **Streak Break** | Missed habit check-in | "Your meditation streak is at risk! Check in today." |
| **Milestone Celebration** | Achievement reached | "🎉 30-day streak on Exercise! Amazing work!" |
| **Recovery Mode** | Low engagement detected | "Let's focus on the basics this week." |

### Coach Personalities

Choose a coaching style that fits you:

- **Balanced**: Moderate interventions, warm tone
- **Intensive**: Frequent check-ins, motivational
- **Minimal**: Only critical interventions
- **Gentle**: Soft approach, encouraging
- **Gamer**: RPG-style language, gamification

### Recovery Modes

The coach automatically adjusts based on your state:

| Mode | When Active | Behavior |
|------|-------------|----------|
| **Push** | Healthy, engaged | Encourage growth |
| **Maintenance** | Stable | Maintain consistency |
| **Recovery** | Stressed, low energy | Reduce pressure |
| **Crisis** | High burnout risk | Minimal interventions |

---

## Weekly Summaries

Automated summaries of your progress, delivered weekly.

### What's Included

- **Overview**: High-level summary of your week
- **Habits**: Streak status, completion rates
- **Tasks**: Completion statistics, overdue items
- **Goals**: Progress updates, upcoming deadlines
- **Health**: Sleep and mood trends
- **Insights**: AI-generated observations
- **Recommendations**: Actionable suggestions

### Accessing Summaries

1. Open AI Assistant
2. Click "Weekly Summary" in the sidebar
3. Or ask: "Show me my weekly summary"

---

## Provider Setup

### Ollama (Recommended for Privacy)

**Pros:**
- Free
- Runs locally
- No internet required
- Complete privacy

**Cons:**
- Requires installation
- Uses your computer's resources
- May be slower than cloud

**Setup:**
```bash
# Install Ollama
# Visit https://ollama.ai

# Start Ollama
ollama serve

# Download a model
ollama pull llama3

# List available models
ollama list
```

### OpenAI (GPT)

**Pros:**
- Most capable models
- Fast responses
- Reliable

**Cons:**
- Requires API key
- Pay per use

**Setup:**
1. Get API key from [OpenAI](https://platform.openai.com/api-keys)
2. Enter in AI Settings or when prompted

**Recommended Models:**
- `gpt-4o`: Most capable (recommended)
- `gpt-4o-mini`: Fast and affordable

### Anthropic (Claude)

**Pros:**
- Excellent reasoning
- Long context window
- Safe outputs

**Cons:**
- Requires API key
- Pay per use

**Setup:**
1. Get API key from [Anthropic](https://console.anthropic.com)
2. Enter in AI Settings

**Recommended Models:**
- `claude-3-5-sonnet`: Best balance (recommended)
- `claude-3-haiku`: Fast and affordable

### Google Gemini

**Pros:**
- Generous free tier
- Long context
- Multimodal

**Cons:**
- Requires Google account

**Setup:**
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Enter in AI Settings

### Groq

**Pros:**
- Very fast inference
- Good free tier
- Uses open models

**Cons:**
- Limited model selection

**Setup:**
1. Get API key from [Groq](https://console.groq.com/keys)
2. Enter in AI Settings

---

## API Key Management

### Where Keys Are Stored

Your API keys are stored securely:

1. **Environment Variables** (highest priority)
2. **Streamlit Secrets** (if configured)
3. **Encrypted Local File** (`~/.veryfyn/ai_keys.enc`)

### Managing Keys

**In AI Settings:**
- View configured providers
- Add new keys
- Delete existing keys

**Environment Variables:**
```bash
# Set via command line
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Security Best Practices

1. **Never share your API keys**
2. **Rotate keys periodically**
3. **Use environment variables for development**
4. **Delete keys from AI Settings if not needed**

---

## Privacy & Security

### Data Handling

- **Local First**: With Ollama, all processing happens on your machine
- **No Training**: Your data is never used to train AI models
- **Encrypted Storage**: API keys are encrypted locally
- **No Logging**: API keys are never logged

### What's Sent to AI Providers

When using cloud providers, the following is sent:

- Your chat messages
- Relevant context from your tracking data
- System prompts for personalization

**What's NOT sent:**
- Your API keys (only used for authentication)
- Data from other users
- Any data not relevant to your query

### Disabling AI Features

You can disable AI features at any time:

1. Open AI Settings
2. Toggle off specific features
3. Or disable all AI features

### Deleting AI Data

To delete AI-related data:

1. Open AI Settings
2. Click "Clear All Data"
3. Or manually delete:
   - `~/.veryfyn/ai_keys.enc` (API keys)
   - `.veryfyn/chroma_db/` (vector database)

---

## Troubleshooting

### Ollama Not Connecting

1. Ensure Ollama is running: `ollama serve`
2. Check port 11434 is available
3. Verify model is downloaded: `ollama list`

### API Key Not Working

1. Check the key is correct (no extra spaces)
2. Verify the key is active in your provider dashboard
3. Try regenerating the key

### Slow Responses

1. Try a smaller/faster model
2. For Ollama, ensure your system has enough resources
3. Check your internet connection (for cloud providers)

### Context Not Relevant

1. Ensure you have tracking data
2. Try being more specific in your question
3. Check that relevant features are enabled

---

## Getting Help

If you encounter issues:

1. Check this guide
2. Visit the [GitHub Issues](https://github.com/your-repo/issues) page
3. Ask in the community forum

---

*Last updated: February 21, 2026*