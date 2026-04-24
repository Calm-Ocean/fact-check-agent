import streamlit as st
import PyPDF2
from duckduckgo_search import DDGS
import requests
import json
import time # <-- ADDED THIS to handle rate limiting

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Fact-Check Agent", page_icon="🔍", layout="wide")
st.title("🔍 The Fact-Check Agent")
st.markdown("Upload a PDF document, and this tool will extract claims, cross-reference them with live web data, and verify their accuracy.")

# --- API KEY SETUP ---
# The app now securely pulls the key directly from Streamlit secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("🚨 GEMINI_API_KEY is missing from your Streamlit secrets. Please add it to your local .streamlit/secrets.toml file or Streamlit Cloud dashboard to deploy successfully.")
    st.stop()

# --- DIRECT API CALL HELPER ---
def call_gemini(prompt):
    """Bypasses the Python SDK and calls the Gemini REST API directly."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts":[{"text": prompt}]}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        st.error(f"Google API Error: {response.text}")
        return None

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def identify_claims(text):
    prompt = f"""
    Analyze the following text and extract 3 to 5 distinct, verifiable factual claims. 
    Focus on statistics, dates, financial figures, or technical specifications.
    Return ONLY a valid JSON array of strings, where each string is a claim. 
    Example: ["Company X grew by 50% in 2023", "The product costs $400"]
    
    Text:
    {text[:5000]}
    """
    
    raw_response = call_gemini(prompt)
    if not raw_response: return []
    
    try:
        cleaned_response = raw_response.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_response)
    except Exception as e:
        st.error(f"Error parsing claims: {e}")
        return []

def search_web(claim):
    """Searches the web with error handling for rate limits."""
    try:
        results = DDGS().text(claim, max_results=3)
        # Convert results generator to a list to check if it's empty
        results_list = list(results) if results else []
        
        if not results_list:
            return "Web search returned no results (Possible DuckDuckGo rate limit)."
            
        context = ""
        for res in results_list:
            context += f"- {res.get('body', '')}\n"
        return context
    except Exception as e:
        return f"Web search failed due to error: {e}"

def verify_claim(claim, context):
    prompt = f"""
    You are a Fact-Checking Agent. 
    
    Claim: "{claim}"
    Web Context: {context}
    
    INSTRUCTIONS:
    1. First, try to evaluate the claim using the provided Web Context.
    2. FALLBACK: If the Web Context says 'returned no results' or is empty, you MUST use your own internal AI knowledge and historical training data to fact-check the claim.
    
    Classify the claim into exactly one of these categories:
    1. Verified (matches data)
    2. Inaccurate (e.g., outdated stats or slightly wrong)
    3. False (no evidence found or directly contradicted)
    
    Return ONLY a valid JSON object with two keys: "status" and "reason".
    Example: {{"status": "Inaccurate", "reason": "The web shows the stat is actually 30%, not 50%."}}
    """
    
    raw_response = call_gemini(prompt)
    if not raw_response: 
        return {"status": "Error", "reason": "API Failure."}
        
    try:
        cleaned_response = raw_response.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_response)
    except Exception as e:
        return {"status": "Error", "reason": "Could not process the verification."}

# --- MAIN APP UI ---
uploaded_file = st.file_uploader("Upload a PDF document containing marketing claims", type=["pdf"])

if uploaded_file is not None:
    if st.button("Start Fact-Checking"):
        with st.status("Analyzing document...", expanded=True) as status:
            st.write("Extracting text from PDF...")
            document_text = extract_text_from_pdf(uploaded_file)
            
            st.write("Identifying factual claims...")
            claims = identify_claims(document_text)
            
            if not claims:
                st.error("No clear claims could be extracted.")
                st.stop()
            
            st.write("Searching the live web and verifying...")
            final_results = []
            for claim in claims:
                
                # --- THE FIX: Slow down the loop so DuckDuckGo doesn't block us ---
                time.sleep(2.5) 
                
                web_context = search_web(claim)
                verification = verify_claim(claim, web_context)
                final_results.append({
                    "claim": claim,
                    "status": verification.get("status", "Unknown"),
                    "reason": verification.get("reason", "No reason provided.")
                })
            status.update(label="Fact-Checking Complete!", state="complete", expanded=False)

        # --- DISPLAY RESULTS ---
        st.subheader("Fact-Check Report")
        for res in final_results:
            status_color = "🟢" if res['status'] == "Verified" else "🟡" if res['status'] == "Inaccurate" else "🔴"
            
            with st.expander(f"{status_color} {res['status']}: {res['claim']}"):
                st.write(f"**Analysis:** {res['reason']}")