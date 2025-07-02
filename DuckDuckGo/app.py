import streamlit as st
import time
import requests # Assuming you'll use this for your backend API calls

# --- App Configuration (Optional: Set wide mode) ---
st.set_page_config(layout="wide")

# --- App Title ---
st.title("AI-Multi Agent System")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Chat"

# --- Function to start a new chat (for the sidebar button) ---
def new_chat():
    st.session_state.messages = []
    st.session_state.current_chat_title = "New Chat"
    st.rerun() # Rerun to clear the chat window

# --- Sidebar Content ---
with st.sidebar:
    st.image("aii.svg", width=150) # Example logo
    st.markdown("---")

    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_chat()

    st.markdown("---")
    st.subheader("Chats")

    # Simplified Chat History Display
    # In a real app, this would be a list of past conversations loaded from a database
    # For now, we'll just represent the current conversation or some mock entries.
    if st.session_state.messages:
        # Get the first user message as the "chat title"
        first_user_message = next((msg["content"] for msg in st.session_state.messages if msg["role"] == "user"), "Start of Conversation")
        if len(first_user_message) > 30:
            first_user_message = first_user_message[:27] + "..."

        st.markdown(f"**Current Chat:**")
        st.button(first_user_message, key="current_chat_button", use_container_width=True) # A button for the current chat

    else:
        st.markdown("*(No active chat selected)*")

    # Mock other sidebar items for visual similarity
    st.markdown("---")
    st.subheader("Explore")
    st.button("🔍 Search chats", use_container_width=True)
    st.button("📚 Library", use_container_width=True)
    st.button("🤖 GPTs", use_container_width=True)


# --- Main Chat Area Content ---

# Add a Welcome Message if Chat is Empty
if not st.session_state.messages:
    st.markdown(
        """
        <div style="background-color: #e0f2f7; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
            Hello! I'm your AI Multi-Agent System assistant. 🤖
            <br>Ask me anything to get started!
        </div>
        """,
        unsafe_allow_html=True
    )

# Display previous chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input and logic
if prompt := st.chat_input("Ask something..."):
    # 1. Update current chat title if it's the first user message
    if st.session_state.current_chat_title == "New Chat":
        st.session_state.current_chat_title = prompt[:30] + "..." if len(prompt) > 30 else prompt
        st.experimental_rerun() # Rerun to update sidebar title immediately

    # 2. Show user's message and save to session
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Show a loading indicator while processing
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."): # This creates a spinner
            # --- REPLACE THIS WITH YOUR ACTUAL BACKEND API CALL ---
            try:
                backend_url = "http://localhost:5000/api/chat" # Adjust if your backend is elsewhere
                response = requests.post(backend_url, json={"message": prompt})
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                assistant_reply = response.json().get("reply", "No reply from backend.")
            except requests.exceptions.ConnectionError:
                assistant_reply = "Error: Could not connect to the backend API. Is it running?"
            except requests.exceptions.RequestException as e:
                # Attempt to get error message from backend response if available
                try:
                    error_details = e.response.json().get("error", "An unknown error occurred.")
                    assistant_reply = f"Backend error: {error_details}"
                except:
                    assistant_reply = f"An unexpected error occurred: {e}"
            # --- END OF BACKEND API CALL SECTION ---

            st.write(assistant_reply)

    # 4. Save assistant's reply to session
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# --- Clear Chat Button (Optional: you can keep this in main or just rely on sidebar "New Chat") ---
# If you want a quick way to clear chat without navigating, keep this.
# if st.button("Clear Current Chat", type="secondary"):
#     new_chat()