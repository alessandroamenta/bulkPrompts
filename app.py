import streamlit as st
from quick import get_answers as get_answers_async, is_valid_api_key
from sync import get_answers as get_answers_sync 
import pandas as pd
from io import BytesIO
import base64
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛠️ Settings")
API_KEY = st.sidebar.text_input("🔑 OpenAI API Key", value='', type='password')
model_choice = st.sidebar.selectbox("🤖 Choose model:", ["gpt-3.5-turbo-16k", "gpt-4", "gpt-4-1106-preview"])
# Add a slider for temperature setting in the sidebar
temperature = st.sidebar.slider("🌡️ Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
seed = st.sidebar.number_input("🔢 Seed (for deterministic outputs)", min_value=0, max_value=None, value=12345, step=1)
# Add a toggle for choosing between async and sync processing in the sidebar
processing_mode = st.sidebar.selectbox(
    "Select Processing Mode:",
    ["Quick Mode", "High Accuracy Mode"],
    index=1  # Default to slow/accurate
)
# Custom batch size options
batch_size_options = [1] + list(range(5, 51, 5))  # Creates a list [1, 5, 10, 15, ... 50]

if processing_mode == "Quick Mode":
   # Select slider for batch size
    batch_size = st.sidebar.select_slider(
        "Batch Size for Processing",
        options=batch_size_options,
        value=10  # Default value
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
    4. 💨 Select 'Quick Mode' for speed or 'High Accuracy Mode' for precision.
    5. 🔢 Set batch size (only in 'Quick Mode'). 10 is a good default.
    6. ✍️ Add custom instructions for all prompts (if needed).
    7. 📥 Choose the input method: Text Box or File Upload.
    8. 📝 If using Text Box, separate each prompt with a blank line.
    9. 📂 If using File Upload, upload a CSV or Excel file.
    10. 🚀 Click the "Generate Answers" button.
    11. 📤 Once answers are ready, download the Excel file with results.
    """)

st.title("🧠 GPT Answer Generator")
st.write("""
Generate answers for a bulk of prompts using OpenAI.
""")
st.warning("Note: The number of prompts you can process without hitting rate limits may vary. It depends on the complexity of each prompt, the chosen model, and the processing mode. While a larger number of prompts can be processed, especially in 'Quick Mode', be mindful of OpenAI's rate limits. Adjust based on your needs and API response.")


# Radio button to select input method
input_method = st.selectbox("📥 Choose input method:", ["Text Box", "File Upload"])

if input_method == "Text Box":
    st.write("Please separate each prompt with a blank line.")
    user_input = st.text_area("Enter prompts:", height=300)
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
        if processing_mode == "Quick Mode":
            # Asynchronous processing
            with st.spinner('👩‍🍳 GPT is whipping up your answers in batches! Hang tight...'):
                progress_bar = st.progress(0)
                answers = asyncio.run(get_answers_async(prompts, model_choice, common_instructions, API_KEY, temperature, seed, batch_size, progress_bar))
        elif processing_mode == "High Accuracy Mode":
            # Synchronous processing
            with st.spinner('👩‍🍳 GPT is whipping up your answers, one by one! This may take some time...a notification will sound when done.'):
                progress_bar = st.progress(0)
                answers = get_answers_sync(prompts, model_choice, common_instructions, API_KEY, temperature, seed, progress_bar)

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
        autoplay_audio('notification.mp3')  # Play the notification sound

        
        # Display the styled download link directly
        st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="answers.xlsx" style="display: inline-block; padding: 0.25em 0.5em; text-decoration: none; background-color: #4CAF50; color: white; border-radius: 3px; cursor: pointer;">📤 Download Excel File</a>', unsafe_allow_html=True)