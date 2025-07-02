import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS
import webbrowser
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import numpy as np

# Load environment variables if needed
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL_NAME = "models/embedding-001"

# Initialize Gemini embeddings model if API key exists
if GOOGLE_API_KEY:
    gemini_embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=GOOGLE_API_KEY
    )
else:
    gemini_embeddings = None

def perform_search(query, content_type, max_results=3):
    ddgs = DDGS()
    try:
        if content_type == "Text":
            results = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=max_results)
        elif content_type == "Image":
            results = ddgs.images(query, region='wt-wt', safesearch='off', size=None, color=None, type_image=None, layout=None, license_image=None, max_results=max_results)
        elif content_type == "Video":
            results = ddgs.videos(query, region='wt-wt', safesearch='off', max_results=max_results)
        elif content_type == "GIF":
            results = ddgs.images(query, region='wt-wt', safesearch='off', size=None, color=None, type_image='animated', layout=None, license_image=None, max_results=max_results)
        else:
            return []
        return results
    except Exception as e:
        st.error(f"Error performing search: {e}")
        return []

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.find('body').get_text(separator='\n', strip=True) if soup.find('body') else ""
        return main_content
    except Exception as e:
        return f"Error fetching content: {str(e)}"

def generate_embedding(text):
    if not gemini_embeddings:
        return None
    try:
        return gemini_embeddings.embed_query(text)
    except Exception as e:
        return f"Error generating embedding: {str(e)}"

def calculate_similarity(embedding1, embedding2):
    if isinstance(embedding1, str) or isinstance(embedding2, str):
        return -1
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def display_results(results, content_type):
    if not results:
        st.info(f"No {content_type.lower()} results found.")
        return

    if content_type == "Text":
        st.subheader("Top Text Results:")
        for i, result in enumerate(results, 1):
            with st.expander(f"Result {i}: {result['title']}"):
                st.write(result['body'])
                st.write(f"URL: {result.get('url', 'No URL found')}")
                if st.button(f"Open URL {i}", key=f"text_{i}"):
                    webbrowser.open_new_tab(result.get('url', ''))
            st.markdown("---")

    elif content_type == "Image":
        st.subheader("Top Image Results:")
        cols = st.columns(3)
        for i, result in enumerate(results[:3]):
            with cols[i % 3]:
                st.image(result['image'], caption=result['title'])
                st.write(f"Source: {result['url']}")
                if st.button(f"Open Image {i+1}", key=f"image_{i}"):
                    webbrowser.open_new_tab(result['image'])

    elif content_type == "Video":
        st.subheader("Top Video Results:")
        for i, result in enumerate(results, 1):
            with st.expander(f"Video {i}: {result['title']}"):
                st.write(f"Description: {result.get('description', 'No description')}")
                st.write(f"URL: {result.get('content', result.get('url', 'No URL found'))}")
                if st.button(f"Open Video {i}", key=f"video_{i}"):
                    webbrowser.open_new_tab(result.get('content', result.get('url', '')))
            st.markdown("---")

    elif content_type == "GIF":
        st.subheader("Top GIF Results:")
        cols = st.columns(3)
        for i, result in enumerate(results[:3]):
            with cols[i % 3]:
                st.image(result['image'], caption=result['title'])
                st.write(f"Source: {result['url']}")
                if st.button(f"Open GIF {i+1}", key=f"gif_{i}"):
                    webbrowser.open_new_tab(result['image'])

def semantic_search(query, results):
    if not gemini_embeddings:
        return results
    
    query_embedding = generate_embedding(query)
    if isinstance(query_embedding, str):
        return results
    
    enhanced_results = []
    for result in results:
        content = result.get('body', result.get('description', result.get('title', '')))
        content_embedding = generate_embedding(content)
        if not isinstance(content_embedding, str):
            similarity = calculate_similarity(query_embedding, content_embedding)
            enhanced_results.append((result, similarity))
    
    enhanced_results.sort(key=lambda x: x[1], reverse=True)
    return [result for result, _ in enhanced_results]

def save_to_csv(results, content_type, query):
    if not results:
        return
    
    df = pd.DataFrame(results)
    filename = f"{query.replace(' ', '_')}_{content_type.lower()}_results.csv"
    df.to_csv(filename, index=False)
    st.success(f"Results saved to {filename}")
    if st.button(f"Download {content_type} Results CSV"):
        with open(filename, "rb") as f:
            st.download_button(
                label="Click to download",
                data=f,
                file_name=filename,
                mime="text/csv"
            )

def main():
    st.title("🔍 Unified DuckDuckGo Search")
    
    # Sidebar for search options
    with st.sidebar:
        st.header("Search Options")
        content_type = st.selectbox(
            "Search Type:",
            ["Text", "Image", "Video", "GIF"],
            index=0
        )
        max_results = st.slider(
            "Number of results:",
            min_value=1,
            max_value=10,
            value=3,
            help="Select how many results you want to see"
        )
        enable_semantic = False
        if content_type == "Text" and gemini_embeddings:
            enable_semantic = st.checkbox(
                "Enable Semantic Search",
                value=False,
                help="Rank results by semantic similarity to your query (requires Gemini API)"
            )
    
    # Main search interface
    search_query = st.text_input(
        "Enter your search query:",
        placeholder="What are you looking for?"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        search_button = st.button("Search", type="primary")
    with col2:
        clear_button = st.button("Clear")
    
    if clear_button:
        st.rerun()
    
    if search_button or search_query:
        if search_query:
            with st.spinner(f"Searching for {content_type} results..."):
                results = perform_search(search_query, content_type, max_results)
                
                if enable_semantic and content_type == "Text":
                    results = semantic_search(search_query, results)
                
                display_results(results, content_type)
                save_to_csv(results, content_type, search_query)
        else:
            st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()