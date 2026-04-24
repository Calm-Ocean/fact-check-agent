# 🔍 The Fact-Check Agent

An automated "Truth Layer" application built to verify marketing claims, statistics, and figures from PDF documents. 

This tool extracts factual claims from uploaded PDFs and cross-references them against live web data to flag inaccuracies, outdated statistics, or hallucinations.

## ✨ Features

- Automated Extraction:** Reads uploaded PDFs and intelligently identifies 3 to 5 distinct, verifiable factual claims (statistics, dates, financial figures).
- Web Cross-Referencing:** Uses DuckDuckGo to search the live web for context regarding each extracted claim.
- Smart Verification:** Powered by **Google Gemini 2.5 Flash**, it evaluates the claim against the search context (or its own knowledge base if web search is blocked) to classify the claim as:
  - 🟢 Verified: Matches the data.
  - 🟡 Inaccurate: Outdated stats or slightly wrong figures.
  - 🔴 False: No evidence found or directly contradicted.
- Interactive UI: Built with Streamlit for a clean, user-friendly, and responsive interface.

🛠️ Tech Stack

- Frontend/UI: [Streamlit](https://streamlit.io/)
- LLM / Reasoning Engine: [Google Gemini 2.5 Flash API](https://aistudio.google.com/)
- Web Search: DuckDuckGo Search (`duckduckgo-search`)
- PDF Processing: `PyPDF2`
- Language: Python 3.x

## 🚀 Local Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/Calm-Ocean/fact-check-agent.git](https://github.com/Calm-Ocean/fact-check-agent.git)
   cd fact-check-agent
Create and activate a virtual environment:

Bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install the dependencies:

Bash
pip install -r requirements.txt
Set up your API Key:

Get a free API key from Google AI Studio.

Set up a local secrets file so the app can securely access it without exposing the key:

Create a .streamlit folder in your project root.

Inside it, create a file named secrets.toml.

Add this line: GEMINI_API_KEY = "your_actual_api_key_here"

Run the App:

Bash
streamlit run app.py
📖 How to Use
Open the application in your browser (usually http://localhost:8501).

Upload a PDF document containing factual claims or statistics.

Click "Start Fact-Checking".

Expand the results in the Fact-Check Report to read the detailed analysis for each claim.

⚠️ Notes on Rate Limiting
The app uses the free DuckDuckGo search library, which can sometimes rate-limit requests. A time.sleep(2.5) delay has been implemented to mitigate this. If the web search is completely blocked by DuckDuckGo, the app is programmed to intelligently fall back on Gemini 2.5 Flash's internal AI knowledge base to complete the fact-check.
