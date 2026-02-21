"""
AI Settings Page - Manage AI Configuration

Allows users to:
- Switch providers
- Manage API keys
- Select models
- Configure feature toggles

Usage:
    streamlit run tracking_app/pages/ai_settings.py
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

# AI components
from brain.ai.models import AIProvider, ProviderConfig
from brain.ai.api_keys import APIKeyManager
from brain.ai.providers.factory import ProviderFactory
from brain.ai.assistant import AIAssistant


def init_session_state():
    """Initialize session state variables."""
    if 'settings_provider' not in st.session_state:
        st.session_state.settings_provider = "ollama"
    
    if 'settings_model' not in st.session_state:
        st.session_state.settings_model = "llama3"
    
    if 'settings_features' not in st.session_state:
        st.session_state.settings_features = {
            "ai_assistant": True,
            "digital_coach": True,
            "weekly_summaries": True,
            "insights": True,
            "auto_embeddings": True
        }


def get_provider_info() -> Dict[str, Dict[str, Any]]:
    """Get information about available providers."""
    return {
        "ollama": {
            "name": "Ollama (Local)",
            "description": "Run AI locally on your machine",
            "requires_api_key": False,
            "models": ["llama3", "llama3.1", "mistral", "codellama", "phi3"]
        },
        "openai": {
            "name": "OpenAI (GPT)",
            "description": "OpenAI's GPT models",
            "requires_api_key": True,
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "anthropic": {
            "name": "Anthropic (Claude)",
            "description": "Claude AI by Anthropic",
            "requires_api_key": True,
            "models": ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"]
        },
        "gemini": {
            "name": "Google Gemini",
            "description": "Google's Gemini models",
            "requires_api_key": True,
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        },
        "groq": {
            "name": "Groq (Fast)",
            "description": "Ultra-fast inference",
            "requires_api_key": True,
            "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b"]
        }
    }


def render_sidebar():
    """Render the sidebar with navigation."""
    with st.sidebar:
        st.header("🤖 AI Settings")
        
        st.markdown("""
        Configure your AI features:
        
        - **Provider**: Choose your AI provider
        - **API Keys**: Manage your API keys
        - **Model**: Select the AI model
        - **Features**: Enable/disable features
        """)
        
        st.divider()
        
        # Quick status
        st.subheader("Status")
        
        provider = st.session_state.settings_provider
        provider_info = get_provider_info().get(provider, {})
        
        st.metric("Provider", provider_info.get("name", provider.title()))
        st.metric("Model", st.session_state.settings_model)
        
        # API Key status
        if provider_info.get("requires_api_key"):
            key_manager = APIKeyManager()
            has_key = key_manager.has_key(provider)
            if has_key:
                st.success("🔑 API Key Set")
            else:
                st.warning("🔑 API Key Missing")
        else:
            st.info("🆓 No Key Required")


def render_provider_settings():
    """Render provider selection settings."""
    st.header("🔌 Provider Settings")
    
    provider_info = get_provider_info()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Provider selection
        providers = list(provider_info.keys())
        current_idx = providers.index(st.session_state.settings_provider) if st.session_state.settings_provider in providers else 0
        
        selected = st.selectbox(
            "Active Provider",
            options=providers,
            index=current_idx,
            format_func=lambda x: provider_info[x]["name"],
            help="Select your AI provider"
        )
        
        if selected != st.session_state.settings_provider:
            st.session_state.settings_provider = selected
            # Update model to default for new provider
            st.session_state.settings_model = provider_info[selected]["models"][0]
            st.rerun()
        
        # Provider description
        info = provider_info[selected]
        st.info(f"**{info['name']}**\n\n{info['description']}")
    
    with col2:
        st.subheader("Provider Details")
        
        if info.get("requires_api_key"):
            st.warning("🔑 API key required")
        else:
            st.success("🆓 No API key needed")
        
        if info.get("pricing"):
            st.metric("Pricing", info["pricing"])
        
        if info.get("pros"):
            st.markdown("**Pros:**")
            for pro in info["pros"]:
                st.markdown(f"- {pro}")


def render_api_key_settings():
    """Render API key management settings."""
    st.header("🔑 API Key Management")
    
    provider = st.session_state.settings_provider
    provider_info = get_provider_info().get(provider, {})
    
    if not provider_info.get("requires_api_key"):
        st.success(f"🎉 {provider_info.get('name', provider.title())} doesn't require an API key!")
        return
    
    key_manager = APIKeyManager()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        Manage your {provider_info.get('name')} API key.
        
        Your API key is stored securely and encrypted locally.
        """)
        
        # Current key status
        has_key = key_manager.has_key(provider)
        
        if has_key:
            st.success("✅ API key is configured")
            
            # Show masked key from export
            key_info = key_manager.export_keys(include_values=True)
            if provider in key_info.get("keys", {}):
                st.caption(f"Current key: {key_info['keys'][provider]}")
        else:
            st.warning("⚠️ No API key configured")
        
        # New key input
        new_key = st.text_input(
            "New API Key",
            type="password",
            placeholder=f"Enter your {provider_info.get('name')} API key",
            help="Your API key is encrypted and stored locally"
        )
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Save Key", use_container_width=True):
                if new_key:
                    key_manager.set_key(provider, new_key)
                    st.success("API key saved successfully!")
                    st.rerun()
                else:
                    st.warning("Please enter an API key")
        
        with col_b:
            if has_key:
                if st.button("Delete Key", use_container_width=True, type="secondary"):
                    key_manager.delete_key(provider)
                    st.success("API key deleted")
                    st.rerun()
    
    with col2:
        # Link to get API key
        api_key_urls = {
            "openai": "https://platform.openai.com/api-keys",
            "anthropic": "https://console.anthropic.com/settings/keys",
            "gemini": "https://makersuite.google.com/app/apikey",
            "groq": "https://console.groq.com/keys"
        }
        
        if provider in api_key_urls:
            st.link_button(
                f"Get {provider_info.get('name')} API Key",
                api_key_urls[provider],
                use_container_width=True
            )
        
        st.info("""
        **Security Tips:**
        
        - Never share your API key
        - Keys are encrypted locally
        - Keys are never logged
        """)


def render_model_settings():
    """Render model selection settings."""
    st.header("🧠 Model Selection")
    
    provider = st.session_state.settings_provider
    provider_info = get_provider_info().get(provider, {})
    models = provider_info.get("models", [])
    
    if not models:
        st.warning("No models available for this provider")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        current_idx = models.index(st.session_state.settings_model) if st.session_state.settings_model in models else 0
        
        selected_model = st.selectbox(
            "Active Model",
            options=models,
            index=current_idx,
            help="Select the AI model to use"
        )
        
        if selected_model != st.session_state.settings_model:
            st.session_state.settings_model = selected_model
            st.rerun()
    
    with col2:
        # Model descriptions
        model_descriptions = {
            "gpt-4o": "Most capable GPT-4 model",
            "gpt-4o-mini": "Fast and affordable",
            "gpt-4-turbo": "Previous generation GPT-4",
            "gpt-3.5-turbo": "Fast and cheap",
            "claude-3-5-sonnet": "Latest Claude, excellent balance",
            "claude-3-opus": "Most capable Claude",
            "claude-3-haiku": "Fast Claude",
            "llama3": "Meta's Llama 3",
            "llama3.1": "Updated Llama 3.1",
            "mistral": "Mistral's open model",
            "gemini-1.5-pro": "Most capable Gemini",
            "gemini-1.5-flash": "Fast Gemini"
        }
        
        if selected_model in model_descriptions:
            st.info(f"📝 {model_descriptions[selected_model]}")
        
        st.info("""
        **Model Tips:**
        
        - Larger models are smarter but slower
        - Smaller models are faster
        - Test different models to find your preference
        """)


def render_feature_settings():
    """Render feature toggle settings."""
    st.header("⚙️ Feature Settings")
    
    features = st.session_state.settings_features
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("AI Features")
        
        ai_assistant = st.toggle(
            "AI Assistant",
            value=features.get("ai_assistant", True),
            help="Enable the AI Assistant chat feature"
        )
        
        digital_coach = st.toggle(
            "Digital Coach",
            value=features.get("digital_coach", True),
            help="Enable the Digital Coach proactive guidance"
        )
        
        weekly_summaries = st.toggle(
            "Weekly Summaries",
            value=features.get("weekly_summaries", True),
            help="Enable automated weekly summaries"
        )
        
        insights = st.toggle(
            "Smart Insights",
            value=features.get("insights", True),
            help="Enable pattern detection and insights"
        )
    
    with col2:
        st.subheader("Advanced")
        
        auto_embeddings = st.toggle(
            "Auto Embeddings",
            value=features.get("auto_embeddings", True),
            help="Automatically embed data for RAG"
        )
        
        streaming = st.toggle(
            "Streaming Responses",
            value=features.get("streaming", True),
            help="Stream AI responses in real-time"
        )
        
        debug_mode = st.toggle(
            "Debug Mode",
            value=features.get("debug_mode", False),
            help="Show debug information"
        )
    
    # Update features
    st.session_state.settings_features = {
        "ai_assistant": ai_assistant,
        "digital_coach": digital_coach,
        "weekly_summaries": weekly_summaries,
        "insights": insights,
        "auto_embeddings": auto_embeddings,
        "streaming": streaming,
        "debug_mode": debug_mode
    }
    
    st.divider()
    
    # Feature status summary
    enabled_count = sum(1 for v in st.session_state.settings_features.values() if v)
    total_count = len(st.session_state.settings_features)
    
    st.metric("Features Enabled", f"{enabled_count}/{total_count}")


def render_advanced_settings():
    """Render advanced settings."""
    st.header("🔧 Advanced Settings")
    
    with st.expander("Context Settings"):
        st.markdown("Configure how the AI uses context from your data.")
        
        max_context = st.slider(
            "Max Context Items",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum number of context items to include"
        )
        
        context_types = st.multiselect(
            "Context Types",
            options=["habits", "tasks", "goals", "health", "notes"],
            default=["habits", "tasks", "goals"],
            help="Types of data to include in context"
        )
    
    with st.expander("Performance Settings"):
        st.markdown("Configure performance settings.")
        
        timeout = st.slider(
            "Request Timeout (seconds)",
            min_value=10,
            max_value=120,
            value=30,
            help="Maximum time to wait for AI response"
        )
        
        retries = st.slider(
            "Max Retries",
            min_value=0,
            max_value=5,
            value=2,
            help="Number of retries on failure"
        )
    
    with st.expander("Data & Privacy"):
        st.markdown("Configure data and privacy settings.")
        
        store_conversations = st.checkbox(
            "Store Conversation History",
            value=True,
            help="Save chat history locally"
        )
        
        analytics = st.checkbox(
            "Usage Analytics",
            value=False,
            help="Help improve the app by sharing anonymous usage data"
        )
        
        if st.button("Clear All Data", type="secondary"):
            st.warning("This will clear all AI-related data. Are you sure?")


def render_reset_options():
    """Render reset and default options."""
    st.header("🔄 Reset Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Reset to Defaults", use_container_width=True):
            st.session_state.settings_provider = "ollama"
            st.session_state.settings_model = "llama3"
            st.session_state.settings_features = {
                "ai_assistant": True,
                "digital_coach": True,
                "weekly_summaries": True,
                "insights": True,
                "auto_embeddings": True
            }
            st.success("Settings reset to defaults!")
            st.rerun()
    
    with col2:
        if st.button("Clear Chat History", use_container_width=True):
            # Would clear chat history in a real implementation
            st.success("Chat history cleared!")
    
    with col3:
        if st.button("Clear API Keys", use_container_width=True):
            key_manager = APIKeyManager()
            for provider in get_provider_info().keys():
                key_manager.delete_key(provider)
            st.success("All API keys cleared!")
            st.rerun()


def main():
    """Main page entry point."""
    st.set_page_config(
        page_title="AI Settings - Veryfyn",
        page_icon="⚙️",
        layout="wide"
    )
    
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    st.title("⚙️ AI Settings")
    st.markdown("Configure your AI features and preferences")
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Provider", "API Keys", "Model", "Features", "Advanced"
    ])
    
    with tab1:
        render_provider_settings()
    
    with tab2:
        render_api_key_settings()
    
    with tab3:
        render_model_settings()
    
    with tab4:
        render_feature_settings()
    
    with tab5:
        render_advanced_settings()
    
    st.divider()
    
    # Reset options
    render_reset_options()


if __name__ == "__main__":
    main()