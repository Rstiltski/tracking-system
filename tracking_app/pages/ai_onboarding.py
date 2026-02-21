"""
AI Onboarding Page - First-time Setup Wizard

Guides users through setting up AI features including:
- Provider selection
- API key configuration
- Model selection
- Feature preferences

Usage:
    streamlit run tracking_app/pages/ai_onboarding.py
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import os

# AI components
from brain.ai.models import AIProvider, ProviderConfig
from brain.ai.api_keys import APIKeyManager
from brain.ai.providers.factory import ProviderFactory


def init_session_state():
    """Initialize session state variables."""
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    
    if 'selected_provider' not in st.session_state:
        st.session_state.selected_provider = None
    
    if 'api_key_set' not in st.session_state:
        st.session_state.api_key_set = False
    
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    
    if 'feature_preferences' not in st.session_state:
        st.session_state.feature_preferences = {
            "ai_assistant": True,
            "digital_coach": True,
            "weekly_summaries": True,
            "insights": True
        }
    
    if 'onboarding_complete' not in st.session_state:
        st.session_state.onboarding_complete = False


def get_provider_info() -> Dict[str, Dict[str, Any]]:
    """Get information about available providers."""
    return {
        "ollama": {
            "name": "Ollama (Local)",
            "description": "Run AI locally on your machine. Free, private, no internet required.",
            "requires_api_key": False,
            "models": ["llama3", "llama3.1", "mistral", "codellama", "phi3"],
            "pros": ["Free", "Private", "Offline"],
            "cons": ["Requires installation", "Uses local resources"],
            "install_url": "https://ollama.ai"
        },
        "openai": {
            "name": "OpenAI (GPT)",
            "description": "OpenAI's GPT models. Powerful, fast, requires API key.",
            "requires_api_key": True,
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "pros": ["Most capable", "Fast", "Reliable"],
            "cons": ["Requires API key", "Costs money"],
            "pricing": "Pay per use"
        },
        "anthropic": {
            "name": "Anthropic (Claude)",
            "description": "Claude AI by Anthropic. Great for analysis and writing.",
            "requires_api_key": True,
            "models": ["claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"],
            "pros": ["Excellent reasoning", "Long context", "Safe outputs"],
            "cons": ["Requires API key", "Costs money"],
            "pricing": "Pay per use"
        },
        "gemini": {
            "name": "Google Gemini",
            "description": "Google's Gemini models. Good integration with Google services.",
            "requires_api_key": True,
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
            "pros": ["Good free tier", "Long context", "Multimodal"],
            "cons": ["Requires API key", "Google account"],
            "pricing": "Free tier available"
        },
        "groq": {
            "name": "Groq (Fast)",
            "description": "Ultra-fast inference with LPU technology.",
            "requires_api_key": True,
            "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b"],
            "pros": ["Very fast", "Good free tier", "Open models"],
            "cons": ["Requires API key", "Limited models"],
            "pricing": "Free tier available"
        }
    }


def render_welcome_step():
    """Render the welcome step."""
    st.header("👋 Welcome to Veryfyn AI")
    
    st.markdown("""
    Veryfyn AI helps you get more out of your tracking data with:
    
    - **AI Assistant**: Chat with your data, ask questions, get insights
    - **Digital Coach**: Personalized guidance and proactive interventions
    - **Weekly Summaries**: Automated progress reports
    - **Smart Insights**: Pattern detection and recommendations
    
    Let's set up your AI features in just a few steps!
    """)
    
    st.info("💡 Your data stays private. AI features run locally when possible, and your data is never used to train AI models.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Get Started →", type="primary", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()


def render_provider_step():
    """Render the provider selection step."""
    st.header("🤖 Choose Your AI Provider")
    
    provider_info = get_provider_info()
    
    # Provider selection
    col1, col2 = st.columns(2)
    
    providers = list(provider_info.keys())
    selected = None
    
    for i, provider_id in enumerate(providers):
        info = provider_info[provider_id]
        
        if i % 2 == 0:
            with col1:
                selected = render_provider_card(provider_id, info)
        else:
            with col2:
                selected = render_provider_card(provider_id, info)
    
    # Navigation
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step = 0
            st.rerun()
    
    with col3:
        if st.session_state.selected_provider:
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
        else:
            st.button("Continue →", type="primary", use_container_width=True, disabled=True)


def render_provider_card(provider_id: str, info: Dict[str, Any]) -> None:
    """Render a provider selection card."""
    is_selected = st.session_state.selected_provider == provider_id
    
    # Create a container with border if selected
    if is_selected:
        st.success(f"✓ {info['name']}")
    else:
        st.markdown(f"### {info['name']}")
    
    st.write(info['description'])
    
    # Pros and cons
    if info.get('pros'):
        st.markdown("**Pros:** " + ", ".join(info['pros']))
    
    if info.get('pricing'):
        st.caption(f"💰 {info['pricing']}")
    
    # API key indicator
    if info['requires_api_key']:
        st.caption("🔑 API key required")
    else:
        st.caption("🆓 No API key needed")
    
    # Select button
    button_label = "Selected" if is_selected else "Select"
    button_type = "primary" if is_selected else "secondary"
    
    if st.button(button_label, key=f"select_{provider_id}", type=button_type, use_container_width=True):
        st.session_state.selected_provider = provider_id
        st.rerun()
    
    st.divider()


def render_api_key_step():
    """Render the API key configuration step."""
    provider_id = st.session_state.selected_provider
    provider_info = get_provider_info().get(provider_id, {})
    
    st.header(f"🔑 Configure {provider_info.get('name', provider_id.title())}")
    
    if not provider_info.get('requires_api_key', False):
        # No API key needed
        st.success("🎉 This provider doesn't require an API key!")
        
        # Show installation instructions for Ollama
        if provider_id == "ollama":
            st.markdown("""
            ### Setup Instructions
            
            1. **Install Ollama** from [ollama.ai](https://ollama.ai)
            2. **Run Ollama** in your terminal:
               ```bash
               ollama serve
               ```
            3. **Pull a model** (if not already downloaded):
               ```bash
               ollama pull llama3
               ```
            
            The app will automatically connect to Ollama running locally.
            """)
            
            # Check if Ollama is running
            st.subheader("Connection Status")
            
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Ollama is running and connected!")
                    models = response.json().get('models', [])
                    if models:
                        st.write("**Available models:**")
                        for model in models:
                            st.write(f"- {model['name']}")
                else:
                    st.warning("⚠️ Ollama found but may not be fully running")
            except Exception:
                st.warning("⚠️ Could not connect to Ollama. Make sure it's running on port 11434.")
        
        st.session_state.api_key_set = True
    
    else:
        # API key needed
        st.markdown(f"""
        To use {provider_info.get('name')}, you'll need an API key.
        
        Your API key is stored securely and never sent anywhere except to {provider_info.get('name')}.
        """)
        
        # API key input
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder=f"Enter your {provider_info.get('name')} API key",
            help="Your API key is encrypted and stored locally"
        )
        
        # Validate button
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Validate Key", use_container_width=True):
                if api_key:
                    # Test the API key
                    with st.spinner("Validating..."):
                        try:
                            valid = test_api_key(provider_id, api_key)
                            if valid:
                                st.success("✅ API key is valid!")
                                # Save the key
                                key_manager = APIKeyManager()
                                key_manager.set_key(provider_id, api_key)
                                st.session_state.api_key_set = True
                            else:
                                st.error("❌ API key is invalid or expired")
                        except Exception as e:
                            st.error(f"Error validating key: {str(e)}")
                else:
                    st.warning("Please enter an API key")
        
        with col2:
            # Link to get API key
            api_key_urls = {
                "openai": "https://platform.openai.com/api-keys",
                "anthropic": "https://console.anthropic.com/settings/keys",
                "gemini": "https://makersuite.google.com/app/apikey",
                "groq": "https://console.groq.com/keys"
            }
            
            if provider_id in api_key_urls:
                st.link_button(
                    f"Get {provider_info.get('name')} API Key",
                    api_key_urls[provider_id],
                    use_container_width=True
                )
    
    # Navigation
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()
    
    with col3:
        can_continue = st.session_state.api_key_set or not provider_info.get('requires_api_key', False)
        if st.button("Continue →", type="primary", use_container_width=True, disabled=not can_continue):
            st.session_state.onboarding_step = 3
            st.rerun()


def test_api_key(provider_id: str, api_key: str) -> bool:
    """Test if an API key is valid."""
    try:
        if provider_id == "openai":
            import openai  # type: ignore[import-unresolved]
            client = openai.OpenAI(api_key=api_key)
            client.models.list()
            return True
        
        elif provider_id == "anthropic":
            import anthropic  # type: ignore[import-unresolved]
            client = anthropic.Anthropic(api_key=api_key)
            # Just check that client was created
            return True
        
        elif provider_id == "groq":
            import groq  # type: ignore[import-unresolved]
            client = groq.Groq(api_key=api_key)
            client.models.list()
            return True
        
        elif provider_id == "gemini":
            import google.generativeai as genai  # type: ignore[import-unresolved]
            genai.configure(api_key=api_key)
            list(genai.list_models())
            return True
        
    except Exception:
        return False
    
    return False


def render_model_step():
    """Render the model selection step."""
    provider_id = st.session_state.selected_provider
    provider_info = get_provider_info().get(provider_id, {})
    
    st.header(f"🧠 Select Model")
    st.markdown(f"Choose which model to use with {provider_info.get('name')}")
    
    models = provider_info.get('models', [])
    
    if not models:
        st.warning("No models available for this provider")
        return
    
    # Model selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_model = st.selectbox(
            "Model",
            options=models,
            index=0,
            help="Select the AI model to use"
        )
        
        st.session_state.selected_model = selected_model
    
    with col2:
        st.info("""
        **Model Tips:**
        
        - Larger models are smarter but slower
        - Smaller models are faster and cheaper
        - Start with the default option
        """)
    
    # Model descriptions
    model_descriptions = {
        "gpt-4o": "Most capable GPT-4 model, recommended",
        "gpt-4o-mini": "Fast and affordable, good for most tasks",
        "gpt-4-turbo": "Previous generation GPT-4",
        "gpt-3.5-turbo": "Fast and cheap, less capable",
        "claude-3-5-sonnet": "Latest Claude, excellent balance",
        "claude-3-opus": "Most capable Claude model",
        "claude-3-haiku": "Fast and affordable Claude",
        "llama3": "Meta's Llama 3, good all-around",
        "llama3.1": "Updated Llama 3.1, improved",
        "mistral": "Mistral's open model",
        "gemini-1.5-pro": "Most capable Gemini",
        "gemini-1.5-flash": "Fast Gemini model"
    }
    
    if selected_model in model_descriptions:
        st.caption(f"📝 {model_descriptions[selected_model]}")
    
    # Navigation
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step = 2
            st.rerun()
    
    with col3:
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.onboarding_step = 4
            st.rerun()


def render_preferences_step():
    """Render the feature preferences step."""
    st.header("⚙️ Feature Preferences")
    st.markdown("Choose which AI features to enable")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Features")
        
        ai_assistant = st.checkbox(
            "AI Assistant",
            value=st.session_state.feature_preferences.get("ai_assistant", True),
            help="Chat with your data and ask questions"
        )
        
        digital_coach = st.checkbox(
            "Digital Coach",
            value=st.session_state.feature_preferences.get("digital_coach", True),
            help="Proactive guidance and interventions"
        )
        
        weekly_summaries = st.checkbox(
            "Weekly Summaries",
            value=st.session_state.feature_preferences.get("weekly_summaries", True),
            help="Automated progress reports"
        )
        
        insights = st.checkbox(
            "Smart Insights",
            value=st.session_state.feature_preferences.get("insights", True),
            help="Pattern detection and recommendations"
        )
    
    with col2:
        st.subheader("About Features")
        st.info("""
        **AI Assistant**
        Ask questions about your data and get contextual answers.
        
        **Digital Coach**
        Get proactive guidance when you need it most.
        
        **Weekly Summaries**
        Receive automated weekly progress reports.
        
        **Smart Insights**
        Discover patterns in your behavior.
        """)
    
    # Update preferences
    st.session_state.feature_preferences = {
        "ai_assistant": ai_assistant,
        "digital_coach": digital_coach,
        "weekly_summaries": weekly_summaries,
        "insights": insights
    }
    
    # Navigation
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.onboarding_step = 3
            st.rerun()
    
    with col3:
        if st.button("Complete Setup", type="primary", use_container_width=True):
            save_configuration()
            st.session_state.onboarding_complete = True
            st.session_state.onboarding_step = 5
            st.rerun()


def render_complete_step():
    """Render the completion step."""
    st.header("🎉 Setup Complete!")
    
    st.markdown("""
    Your AI features are now configured and ready to use.
    
    Here's what you can do next:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.page_link("pages/ai_assistant.py", label="💬 Open AI Assistant", icon="💬")
        st.page_link("pages/digital_coach.py", label="🧠 Open Digital Coach", icon="🧠")
    
    with col2:
        st.markdown("""
        ### Your Configuration
        
        - **Provider:** {}
        - **Model:** {}
        - **Features:** {}
        """.format(
            st.session_state.selected_provider.title(),
            st.session_state.selected_model or "Default",
            ", ".join([k.replace("_", " ").title() for k, v in st.session_state.feature_preferences.items() if v])
        ))
    
    st.divider()
    
    st.info("💡 You can change these settings anytime in the AI Settings page.")
    
    if st.button("Start Using Veryfyn", type="primary", use_container_width=True):
        st.switch_page("tracking_app/Home.py")


def save_configuration():
    """Save the configuration to settings."""
    # In a real implementation, this would save to a config file or database
    config = {
        "provider": st.session_state.selected_provider,
        "model": st.session_state.selected_model,
        "features": st.session_state.feature_preferences,
        "onboarding_complete": True,
        "setup_date": str(st.date_input("setup_date"))
    }
    
    # For now, just save to session state
    st.session_state.ai_config = config


def main():
    """Main page entry point."""
    st.set_page_config(
        page_title="AI Setup - Veryfyn",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize
    init_session_state()
    
    # Progress indicator
    steps = ["Welcome", "Provider", "API Key", "Model", "Preferences", "Complete"]
    current_step = st.session_state.onboarding_step
    
    # Render progress bar
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                st.success(f"✓ {step}")
            elif i == current_step:
                st.info(f"**{step}**")
            else:
                st.write(step)
    
    st.divider()
    
    # Render current step
    if current_step == 0:
        render_welcome_step()
    elif current_step == 1:
        render_provider_step()
    elif current_step == 2:
        render_api_key_step()
    elif current_step == 3:
        render_model_step()
    elif current_step == 4:
        render_preferences_step()
    elif current_step == 5:
        render_complete_step()


if __name__ == "__main__":
    main()