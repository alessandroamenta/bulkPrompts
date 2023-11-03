import streamlit as st
from openai_handler import get_answers as get_answers_async, is_valid_api_key
from sync import get_answers as get_answers_sync 
import pandas as pd
from io import BytesIO
import base64
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
 
# Sidebar
st.sidebar.title("🛠️ Settings")
API_KEY = st.sidebar.text_input("🔑 OpenAI API Key", value='', type='password')
model_choice = st.sidebar.selectbox("🤖 Choose model:", ["gpt-3.5-turbo-16k", "gpt-4"])
# Add a slider for temperature setting in the sidebar
temperature = st.sidebar.slider("🌡️ Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
# Add a toggle for choosing between async and sync processing in the sidebar
processing_mode = st.sidebar.radio(
    "Choose processing mode:",
    ("Async", "Sync"),
    index=0  # Default to Asynchronous
)
# Add a text area for common instructions in the sidebar
with st.sidebar.expander("📝 Custom Instructions"):
    common_instructions = st.text_area(
        "Enter instructions to apply to all prompts (e.g., 'You are an expert copywriter, respond in Dutch.')",
        ''
    )

# Instructions Expander
with st.sidebar.expander("🔍 How to use"):
    st.write("""
    1. 🔑 Input your OpenAI API key.
    2. 🤖 Pick the model.
    3. 🌡️ Adjust the temperature to tweak creativity.
    4. ✍️ Add custom instructions for all prompts (if needed).
    5. 📥 Choose the input method: Text Box or File Upload.
    6. 📝 If using Text Box, separate each prompt with a blank line.
    7. 📂 If using File Upload, upload a CSV or Excel file.
    8. 🚀 Click the "Generate Answers" button.
    9. 📤 Once answers are ready, download the Excel file with results.
    """)

st.title("🧠 GPT Answer Generator")
st.write("""
Generate answers for up to 50 prompts using OpenAI.
""")
st.warning("For best performance and to stay within OpenAI's rate limits, limit to 50 prompts.")

# Radio button to select input method
input_method = st.radio("📥 Choose input method:", ["Text Box", "File Upload"])

if input_method == "Text Box":
    st.write("Please separate each prompt with a blank line.")
    user_input = st.text_area("Enter up to 50 prompts:", height=300)
    prompts = user_input.split('\n\n')  # Split by two newlines
    logging.info(f"Prompts from text box: {prompts}")

elif input_method == "File Upload":
    uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        prompts = df.iloc[:, 0].tolist()  # Read prompts from the first column
        logging.info(f"Prompts from file upload: {prompts}")

else:
    prompts = []

# Button to generate answers
if st.button("🚀 Generate Answers"):
    if not API_KEY:
        st.error("You forgot to add your API key, please add it and try again! :)")
    elif not asyncio.run(is_valid_api_key(API_KEY)):
        st.error("The API key provided is not valid. Please check your key and try again.")
    else:
        if processing_mode == "Async":
            # Asynchronous processing
            with st.spinner('👩‍🍳 GPT is whipping up your answers asynchronously! Hang tight...'):
                answers = asyncio.run(get_answers_async(prompts, model_choice, common_instructions, API_KEY, temperature))
        elif processing_mode == "Sync":
            # Synchronous processing
            with st.spinner('👩‍🍳 GPT is whipping up your answers synchronously! This may take some time...'):
                answers = get_answers_sync(prompts, model_choice, common_instructions, API_KEY, temperature)

        logging.info(f"Answers received: {answers}")

        # Create a DataFrame
        df = pd.DataFrame({
            'Prompts': prompts,
            'Answers': answers
        })
        
        # Convert DataFrame to Excel and let the user download it
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

        excel_data = output.getvalue()
        b64 = base64.b64encode(excel_data).decode('utf-8') 
        
        st.success("🎉 Answers generated successfully!")
        
        # Display the styled download link directly
        st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="answers.xlsx" style="display: inline-block; padding: 0.25em 0.5em; text-decoration: none; background-color: #4CAF50; color: white; border-radius: 3px; cursor: pointer;">📤 Download Excel File</a>', unsafe_allow_html=True)