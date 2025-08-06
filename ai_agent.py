import streamlit as st
import pandas as pd
from openai import OpenAI
import io
import os

# Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Business Agent", layout="centered")
st.title("🤖 AI Business Agent")

st.write("Draft humanized responses or parse addresses into columns for Google Sheets.")

# ----------------------------
# FUNCTIONS
# ----------------------------

def draft_response(text):
    """Generate a unique, human-like response with error handling."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # use gpt-4o for better availability
            messages=[
                {"role": "system", "content": "You are a helpful AI that writes professional, human-like responses."},
                {"role": "user", "content": f"Write a friendly and professional reply to:\n\n{text}"}
            ],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        # Return the error message in the app for easier debugging
        return f"❌ API Error: {str(e)}"

def parse_addresses(df):
    """Split addresses into Street and City/State/ZIP"""
    parsed_data = []
    for address in df.iloc[:,0].dropna():
        parts = address.rsplit(",", 2)
        if len(parts) == 3:
            street = parts[0].strip()
            city_state_zip = f"{parts[1].strip()}, {parts[2].strip()}"
            parsed_data.append([street, city_state_zip])
        else:
            parsed_data.append([address, ""])
    return pd.DataFrame(parsed_data, columns=["Street Address", "City, State, ZIP"])

# ----------------------------
# INTERFACE
# ----------------------------

tab1, tab2 = st.tabs(["✍️ Draft Response", "📄 Parse Addresses"])

# Tab 1: Humanized Responses
with tab1:
    st.subheader("Draft a Response to a Review or Email")
    user_text = st.text_area("Paste the content here:", height=150)
    
    if st.button("Generate Response"):
        if user_text.strip():
            with st.spinner("Crafting your response..."):
                reply = draft_response(user_text)
            st.success("✅ Response Generated (or Error Below)")
            st.text_area("AI Response / Debug Output:", reply, height=150)
        else:
            st.warning("Please enter some text first.")

# Tab 2: Address Parsing
with tab2:
    st.subheader("Upload CSV with Addresses")
    uploaded_file = st.file_uploader("Upload CSV (1 column of full addresses)", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Data:")
        st.dataframe(df.head())
        
        if st.button("Parse Addresses"):
            with st.spinner("Parsing addresses..."):
                parsed_df = parse_addresses(df)
            st.success("✅ Parsing Complete!")
            st.dataframe(parsed_df.head())

            # Download button
            csv_buffer = io.StringIO()
            parsed_df.to_csv(csv_buffer, index=False)
            st.download_button("⬇️ Download Parsed CSV", csv_buffer.getvalue(), "parsed_addresses.csv", "text/csv")
