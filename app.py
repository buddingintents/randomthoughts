import streamlit as st
import requests
import base64
import io
from PIL import Image

# Configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Read API keys from Streamlit secrets
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

def generate_trivia():
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """Generate a random trivia fact. Make it either:
    - Sarcastically humorous with a dark twist
    - Surprisingly informative with a niche fact
    Keep it concise (15-25 words)."""
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Trivia generation failed: {str(e)}")
        return None

def generate_image(prompt):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": f"Minimalistic abstract background representing: {prompt}. No text, subtle patterns, soft colors.",
    }
    
    try:
        response = requests.post(IMAGE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None

def create_card(trivia, image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Create HTML card with background image
    card_html = f"""
    <div style="
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('data:image/png;base64,{img_str}');
        background-size: cover;
        background-position: center;
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    ">
        <blockquote style="
            font-size: 1.5rem;
            font-weight: 500;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            max-width: 800px;
            margin: 0;
        ">
            "{trivia}"
        </blockquote>
    </div>
    """
    return card_html

# Streamlit UI
st.title("🤖 Snarky Facts Generator")
st.write("Get AI-generated trivia with attitude and matching visuals!")

if st.button("Generate Mind-Blowing Fact"):
    with st.spinner("Crafting witty wisdom..."):
        trivia = generate_trivia()
    
    if trivia:
        with st.spinner("Painting masterpiece..."):
            image_data = generate_image(trivia)
        
        if image_data:
            st.balloons()
            card = create_card(trivia, image_data)
            st.markdown(card, unsafe_allow_html=True)
            
            # Add download button
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Image",
                    data=image_data,
                    file_name="trivia_card.png",
                    mime="image/png"
                )
            with col2:
                st.download_button(
                    label="Download Text",
                    data=trivia,
                    file_name="trivia_quote.txt",
                    mime="text/plain"
                )
