import streamlit as st
import requests
import json
import os
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = os.getenv("BACKEND_SERVICE_URL", "http://0.0.0.0:8888/v1/vocab_generator")

# Page config
st.set_page_config(
    page_title="Japanese Vocabulary Generator",
    page_icon="🇯🇵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def fetch_vocabulary(topic: str, word_count: int) -> Optional[Dict]:
    """Fetch vocabulary from backend service"""
    try:
        response = requests.post(
            BACKEND_URL,
            json={"topic": topic, "word_count": word_count},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to backend service. Please try again later.")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {str(e)}")
    return None

def display_word_cards(words: List[Dict]):
    """Display vocabulary words in card format"""
    cols = st.columns(3)
    for idx, word in enumerate(words):
        with cols[idx % 3]:
            container = st.container()
            container.markdown(f"""
            **Japanese:** {word["japanese"]}  
            **Romaji:** {word["romaji"]}  
            **English:** {word["english"]}  
            **Type:** {word["parts"]["type"]}  
            **Formality:** {word["parts"]["formality"]}
            """)

def main():
    # Main content
    st.title("Japanese Vocabulary Generator")
    
    # Input form
    with st.form("vocab_form"):
        topic = st.text_input(
            "Enter a topic",
            max_chars=50,
            placeholder="e.g., Basic Greetings, Food and Drinks, Weather"
        )
        
        word_count = st.slider(
            "Number of words",
            min_value=3,
            max_value=10,
            value=5
        )
        
        submit = st.form_submit_button("Generate Vocabulary")
        
    if submit:
        if not topic:
            st.error("Please enter a topic")
        else:
            with st.spinner("Generating vocabulary..."):
                result = fetch_vocabulary(topic, word_count)
                
            if result:
                st.subheader(f"Vocabulary for: {result['group_name']}")
                
                # Collapsible JSON view
                with st.expander("View Raw JSON"):
                    st.code(json.dumps(result), language="json")
                
                # Display word cards
                display_word_cards(result['words'])

if __name__ == "__main__":
    main() 