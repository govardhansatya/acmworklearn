import streamlit as st
import requests
from config.settings import LINKEDIN_ACCESS_TOKEN

def search_linkedin(keyword):
    # Simulated search; LinkedIn official API requires partnership
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
    }
    # Example simulated call — replace with real endpoint once approved
    return [
        {"author": "John Doe", "content": f"Post about {keyword}", "link": "https://linkedin.com/post/123"},
        {"author": "Jane Smith", "content": f"Another {keyword} insight", "link": "https://linkedin.com/post/456"},
    ]

def render_linkedin_ui(user):
    keyword = st.text_input("Enter keyword to track posts")
    if st.button("Search LinkedIn"):
        results = search_linkedin(keyword)
        for r in results:
            st.markdown(f"👤 **{r['author']}**: {r['content']} [🔗 Post]({r['link']})")
