"""
AI Assistant Page - Streamlit UI

Provides a chat interface for interacting with the Veryfyn AI Assistant.
Supports streaming responses, chat history, and source attribution.

Usage:
    Run with: streamlit run tracking_app/pages/ai_assistant.py
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# Try imports with fallbacks for optional dependencies
try:
    from brain.ai.models import ProviderConfig, AIProvider, GenerationResult
    from brain.ai.providers.factory import ProviderFactory
    from brain.ai.vector_store import VectorStore
    from brain.ai.prompts import SystemPromptBuilder
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AI Assistant - Veryfyn",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = str(uuid.uuid4())
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = None
    if "provider_configured" not in st.session_state:
        st.session_state.provider_configured = False


def get_current_messages() -> List[Dict[str, Any]]:
    """Get messages for current session."""
    session_id = st.session_state.current_session_id
    if session_id not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[session_id] = []
    return st.session_state.chat_sessions[session_id]


def add_message(role: str, content: str, sources: Optional[List[Dict]] = None):
    """Add a message to the current session."""
    session_id = st.session_state.current_session_id
    if session_id not in st.session_state.chat_sessions:
        st.session_state.chat_sessions[session_id] = []
    
    st.session_state.chat_sessions[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "sources": sources or []
    })


def clear_current_chat():
    """Clear the current chat session."""
    session_id = st.session_state.current_session_id
    st.session_state.chat_sessions[session_id] = []


def start_new_session():
    """Start a new chat session."""
    st.session_state.current_session_id = str(uuid.uuid4())


# ============================================================================
# AI Provider Configuration
# ============================================================================

def configure_provider() -> Optional[Any]:
    """Configure and return the AI provider."""
    if not AI_AVAILABLE:
        return None
    
    # Get provider settings from sidebar
    provider_type = st.session_state.get("provider_type", "ollama")
    model_name = st.session_state.get("model_name", "llama3")
    api_key = st.session_state.get("api_key", "")
    
    try:
        provider_enum = AIProvider(provider_type)
        config = ProviderConfig(
            provider=provider_enum,
            model=model_name,
            api_key=api_key if api_key else None
        )
        
        if not config.validate():
            return None
        
        return ProviderFactory.create(config)
    except Exception:
        return None


# ============================================================================
# UI Components
# ============================================================================

def render_chat_message(message: Dict[str, Any]):
    """Render a single chat message."""
    role = message["role"]
    content = message["content"]
    sources = message.get("sources", [])
    timestamp = message.get("timestamp", "")
    
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)
            
            # Show sources if available
            if sources:
                with st.expander("📚 Sources", expanded=False):
                    for i, source in enumerate(sources, 1):
                        st.markdown(f"**{i}. {source.get('type', 'Source')}**")
                        st.caption(source.get('content', '')[:200] + "...")
                        st.divider()


def render_chat_history():
    """Render all chat messages."""
    messages = get_current_messages()
    
    if not messages:
        st.info("👋 Start a conversation with your AI assistant!")
        st.markdown("""
        **Things you can ask:**
        - "How am I doing with my habits this week?"
        - "What patterns do you see in my sleep data?"
        - "Help me understand why I'm feeling tired lately"
        - "What goals should I focus on?"
        """)
        return
    
    for message in messages:
        render_chat_message(message)


def render_source_attribution(sources: List[Dict]):
    """Render source attribution for a response."""
    if not sources:
        return
    
    st.markdown("---")
    st.markdown("**📊 Based on:**")
    
    cols = st.columns(min(len(sources), 3))
    for i, source in enumerate(sources[:3]):
        with cols[i]:
            st.caption(f"• {source.get('type', 'Data')}")
            st.caption(f"  {source.get('date', '')}")


def render_sidebar():
    """Render the sidebar with settings and chat history."""
    with st.sidebar:
        st.title("⚙️ AI Settings")
        
        # Provider selection
        st.subheader("Provider")
        provider_type = st.selectbox(
            "Select Provider",
            ["ollama", "openai", "anthropic", "gemini", "groq"],
            key="provider_type",
            help="Ollama runs locally, others require API keys"
        )
        
        # Model selection
        if provider_type == "ollama":
            model_options = ["llama3", "llama3.1", "mistral", "codellama", "phi3"]
        elif provider_type == "openai":
            model_options = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        elif provider_type == "anthropic":
            model_options = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        elif provider_type == "gemini":
            model_options = ["gemini-pro", "gemini-1.5-pro"]
        else:
            model_options = ["llama-3.1-70b", "llama-3.1-8b", "mixtral-8x7b"]
        
        st.selectbox(
            "Select Model",
            model_options,
            key="model_name"
        )
        
        # API Key (for cloud providers)
        if provider_type != "ollama":
            st.text_input(
                "API Key",
                type="password",
                key="api_key",
                help=f"Your {provider_type.capitalize()} API key"
            )
        
        st.divider()
        
        # Chat actions
        st.subheader("Chat Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                clear_current_chat()
                st.rerun()
        
        with col2:
            if st.button("➕ New Session", use_container_width=True):
                start_new_session()
                st.rerun()
        
        st.divider()
        
        # Chat history
        st.subheader("📜 Recent Sessions")
        
        sessions = st.session_state.chat_sessions
        for session_id, messages in list(sessions.items())[-5:]:
            if messages:
                first_msg = messages[0]["content"][:30] + "..."
                is_current = session_id == st.session_state.current_session_id
                
                if st.button(
                    f"{'▶ ' if is_current else ''}{first_msg}",
                    key=f"session_{session_id}",
                    use_container_width=True
                ):
                    st.session_state.current_session_id = session_id
                    st.rerun()
        
        st.divider()
        
        # Status
        st.subheader("📊 Status")
        if AI_AVAILABLE:
            st.success("✅ AI Module Loaded")
        else:
            st.error("❌ AI Module Not Available")
        
        total_messages = sum(
            len(msgs) for msgs in st.session_state.chat_sessions.values()
        )
        st.metric("Total Messages", total_messages)


# ============================================================================
# Main Chat Interface
# ============================================================================

def handle_user_input():
    """Handle user input and generate response."""
    if not AI_AVAILABLE:
        st.error("AI module not available. Please install required dependencies.")
        return
    
    # Configure provider
    provider = configure_provider()
    if provider is None:
        st.error("Please configure a valid AI provider in the sidebar.")
        return
    
    # Get user input
    prompt = st.chat_input("Ask your AI assistant...")
    
    if prompt:
        # Add user message
        add_message("user", prompt)
        
        # Show thinking indicator
        with st.chat_message("assistant", avatar="🤖"):
            thinking = st.empty()
            thinking.markdown("🤔 Thinking...")
            
            try:
                # Initialize provider if needed
                if not provider._is_initialized:
                    provider.initialize()
                
                # Build context (simplified for now)
                context = "User is asking about their personal tracking data."
                system_prompt = SystemPromptBuilder.build(context=context)
                
                # Generate response
                result = provider.generate(
                    prompt=prompt,
                    context=[context]
                )
                
                thinking.empty()
                
                if result.success:
                    st.markdown(result.content)
                    
                    # Add assistant message to history
                    add_message("assistant", result.content)
                else:
                    st.error(f"Error: {result.error_message}")
                    add_message("assistant", f"Sorry, I encountered an error: {result.error_message}")
                    
            except Exception as e:
                thinking.empty()
                st.error(f"Error: {str(e)}")
                add_message("assistant", f"Sorry, an error occurred: {str(e)}")


def main():
    """Main page function."""
    init_session_state()
    
    # Page header
    st.title("🤖 AI Assistant")
    st.caption("Your personal tracking assistant powered by AI")
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    col_main, col_right = st.columns([3, 1])
    
    with col_main:
        # Chat history
        render_chat_history()
        
        # Input handling
        handle_user_input()
    
    with col_right:
        # Quick prompts
        st.subheader("💡 Quick Prompts")
        
        quick_prompts = [
            "How am I doing this week?",
            "Analyze my habits",
            "What should I focus on?",
            "Any patterns in my data?",
        ]
        
        for qp in quick_prompts:
            if st.button(qp, key=f"quick_{qp}", use_container_width=True):
                st.session_state.quick_prompt = qp
                st.rerun()


if __name__ == "__main__":
    main()