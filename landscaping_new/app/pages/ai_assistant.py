"""
AI Assistant Page

Provides an interface to interact with the AI brain system.
"""
from __future__ import annotations
import streamlit as st
from brain import brain_instance
from brain.core.result import ToolOutput

def render_ai_assistant_page() -> None:
    """Render the AI assistant page."""
    st.title("🤖 AI Assistant")
    st.write("Interact with the AI assistant to manage your landscaping business.")
    
    # Initialize chat history in session state if not exists
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, (role, message) in enumerate(st.session_state.ai_chat_history):
            with st.chat_message(role):
                st.write(message)
    
    # Chat input
    with st.form("ai_chat_form"):
        user_input = st.text_input("Ask the AI assistant:", placeholder="e.g., 'Show me all pending jobs' or 'Create a new customer named John Doe'")
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add user message to history
            st.session_state.ai_chat_history.append(("user", user_input))
            
            # Process the user input with the brain system
            try:
                # For demonstration, we'll simulate a response
                # In a real implementation, this would parse the command and execute appropriate tools
                response = process_ai_request(user_input)
                
                # Add AI response to history
                st.session_state.ai_chat_history.append(("assistant", response))
                
                # Rerun to update the UI
                st.rerun()
            except Exception as e:
                error_msg = f"Sorry, I encountered an error processing your request: {str(e)}"
                st.session_state.ai_chat_history.append(("assistant", error_msg))
                st.rerun()
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.ai_chat_history = []
        st.rerun()

def process_ai_request(user_input: str) -> str:
    """
    Process a user request using the brain system.
    
    Args:
        user_input: The user's request
        
    Returns:
        The AI's response
    """
    # This is a simplified implementation
    # In a real system, this would use NLP to parse the request
    # and route to appropriate tools in the brain system
    
    user_input_lower = user_input.lower()
    
    # Simple keyword matching for demonstration
    if "hello" in user_input_lower or "hi" in user_input_lower:
        return "Hello! I'm your landscaping business assistant. How can I help you today?"
    
    elif "pending job" in user_input_lower or "outstanding job" in user_input_lower:
        # Simulate getting pending jobs
        # In real implementation, this would call appropriate tools
        return "I found 3 pending jobs:\n1. Lawn mowing at 123 Main St\n2. Hedge trimming at 456 Oak Ave\n3. Garden cleanup at 789 Pine Rd"
    
    elif "customer" in user_input_lower and ("show" in user_input_lower or "list" in user_input_lower):
        # Simulate getting customers
        return "I found 5 customers in the system:\n1. John Smith\n2. Jane Doe\n3. Bob Johnson\n4. Alice Williams\n5. Charlie Brown"
    
    elif "create customer" in user_input_lower or "add customer" in user_input_lower:
        # This would trigger a customer creation tool in a real implementation
        return "To create a customer, please go to the 'Customers' page and use the 'Add Customer' form."
    
    elif "help" in user_input_lower or "what can you do" in user_input_lower:
        return """I can help you with various tasks:
        - Show pending jobs
        - List customers
        - Provide system information
        - Answer questions about your landscaping business
        
        Try asking: "Show me pending jobs" or "List all customers" """
    
    else:
        # Default response
        return f"I understand you're asking about: '{user_input}'. \n\nCurrently, I can help with basic inquiries. For complex operations, please use the appropriate sections of the application."

def render_brain_status() -> None:
    """Render the status of the brain system."""
    st.subheader("AI System Status")
    
    try:
        status = brain_instance.get_system_status()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Brain ID", status['brain_id'][:8] + "...")
        col2.metric("Tools Available", status['tool_count'])
        col3.metric("Uptime (hrs)", round(status['uptime'] / 3600, 2))
        
        st.success("AI System: Healthy")
    except Exception as e:
        st.error(f"Could not get AI system status: {str(e)}")

# Show brain status
render_brain_status()