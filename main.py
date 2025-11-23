import streamlit as st
from ChatBot import Chatbot
from WeatherBot import WeatherAPI


def initialize_session_state():
    """Initialize session state variables"""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = Chatbot()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    # Page configuration
    st.set_page_config(
        page_title="WeatherBot 🌤️",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("ℹ️ How to Use")
        st.markdown("""
        Welcome to **WeatherBot**! 🤖
        
        Simply type your question in natural language and I'll help you with weather information.
        
        ### 📝 Example Questions:
        
        - *"What's the weather in Paris today?"*
        - *"Will it be hot in New York tomorrow?"*
        - *"When is sunrise in Tokyo on Friday?"*
        - *"Is it going to rain in Berlin today?"*
        - *"What's the temperature in London?"*
        - *"How windy is it in Chicago tomorrow?"*
        
        ### 💬 Other Commands:
        
        - Say hello: *"Hi"*, *"Hello"*
        - Ask how I am: *"How are you?"*
        - Say goodbye: *"Bye"*, *"See you later"*
        - Thank me: *"Thanks"*, *"Thank you"*
        - Ask me for the time (You should try this one)
        
        ---
        
        ### 🌍 Supported Features:
        
        - Weather forecasts for major cities worldwide
        - Temperature, wind, rain, sunrise/sunset info
        - Support for today, tomorrow, or specific weekdays
        - Friendly and funny responses with emojis
        """)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main content
    st.title("🌤️ WeatherBot")
    st.markdown("*Your friendly weather assistant with a sense of humor!*")
    st.divider()
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("Ask me about the weather..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response, intent = st.session_state.chatbot.chat(prompt)
                except Exception as e:
                    response = f"Oops! Something went wrong: {str(e)}"
                    intent = "error"
            
            st.markdown(response)
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update the display
        st.rerun()
    
    # Footer
    st.divider()
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 0.8em;'>"
        "Powered by Open-Meteo API | Built with Streamlit"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
