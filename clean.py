import streamlit as st
import pandas as pd
import os
import json
from Banglanlpdeeplearn.model import model_train
from Banglanlpdeeplearn.text_process import preprocess_text
from Banglanlpdeeplearn.predict import predict_sentiment
import nltk
nltk_data_dir = '/tmp/nltk_data'

# Ensure the directory exists
os.makedirs(nltk_data_dir, exist_ok=True)

# Download the 'punkt' tokenizer to the local directory
nltk.download('punkt', download_dir=nltk_data_dir)

# Append the local directory to NLTK's data path
nltk.data.path.append(nltk_data_dir)
nltk.download('punkt_tab')
# Logo and page config
logo_url = "https://img.freepik.com/free-vector/colorful-bird-illustration-gradient_343694-1741.jpg?size=626&ext=jpg&ga=GA1.1.733875022.1726100029&semt=ais_hybrid.png"
background_image_url = "https://images.unsplash.com/photo-1524758631624-e2822e304c36?crop=entropy&cs=tinysrgb&w=1080&fit=max"

st.set_page_config(page_title="Bangla Sentiment Analysis", page_icon=logo_url, layout="wide")

# Custom CSS for the background image and text styling
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .stButton>button {{
        background-color: #3498db;
        color: white;
        border-radius: 10px;
    }}
    .stButton>button:hover {{
        background-color: #2980b9;
    }}
    .stSidebar {{
        background-color: rgba(0, 0, 0, 0.5);
    }}
    .stTextInput, .stTextArea {{
        background-color: rgba(255, 255, 255, 0.8);
    }}
    h1, h2, h3 {{
        color: white;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.image(logo_url, width=100)

# Load users from JSON file
users_file = 'users.json'
def load_users():
    if os.path.exists(users_file):
        with open(users_file, 'r') as file:
            return json.load(file)
    else:
        return {}

# Save users to JSON file
def save_users(users_db):
    with open(users_file, 'w') as file:
        json.dump(users_db, file)

# Load user database from file
users_db = load_users()

# Caching the data loading function
@st.cache_data
def data_load(file_path):
    df = pd.read_csv(file_path)
    if df.isnull().values.any():
        st.warning("Warning: The dataset contains missing values. Please clean the data.")
    df['processed_text'] = df['text'].apply(preprocess_text)
    return df

# Caching the model training function
@st.cache_resource
def train_model(file_path):
    df = data_load(file_path)
    model1, model2, tokenizer, encoder, X_test, y_test, max_length = model_train(df, 'processed_text', 'label')
    return model1, model2, tokenizer, encoder, X_test, y_test, max_length

# Load the dataset and train models
file_path = "https://raw.githubusercontent.com/alamgirkabirpython/BanglaTextSentiment/main/bangla_sentiment_data.csv"
model1, model2, tokenizer, encoder, X_test, y_test, max_length = train_model(file_path)

# Sidebar: Sign Up and Login
with st.sidebar:
    st.markdown("<h2 style='color:#f1c40f;'>User Authentication</h2>", unsafe_allow_html=True)
    
    # Authentication state management
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "Login"  # Default to Login view

    # Toggle between Login and Sign Up
    auth_mode = st.radio("Select Option:", ["Login", "Sign Up"], key="auth_mode_toggle")

    if auth_mode == "Sign Up":
        st.session_state["auth_mode"] = "Sign Up"
    else:
        st.session_state["auth_mode"] = "Login"

    # Display the form based on the selected mode
    if st.session_state["auth_mode"] == "Sign Up":
        st.write("## Sign Up")
        new_username = st.text_input("Choose a Username", key="signup_username")
        new_password = st.text_input("Choose a Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            if new_username in users_db:
                st.warning("Username already exists. Please choose a different username.")
            elif new_username and new_password:
                users_db[new_username] = new_password
                save_users(users_db)
                st.success("Sign up successful! You can now log in.")
            else:
                st.error("Please fill both fields.")

    elif st.session_state["auth_mode"] == "Login":
        st.write("## Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_username in users_db and users_db[login_username] == login_password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = login_username
                st.success(f"Welcome {login_username}! You are now logged in.")
            else:
                st.error("Invalid username or password.")

    # Contact details
    st.write("## Contact")
    st.write("**Email:** alomgirkabir720@gmail.com")
    st.write("**Phone:** 01743296524")

# Main page content
st.title("Bangla Sentiment Analysis :heart_eyes: :cry:")

if st.session_state["authenticated"]:
    # Sidebar for model selection (only accessible after login)
    with st.sidebar:
        st.markdown("<h2 style='color:#f1c40f;'>Model Configuration</h2>", unsafe_allow_html=True)
        model_choice = st.selectbox("Choose a model:", ['Model 1', 'Model 2'])
        model = model1 if model_choice == 'Model 1' else model2

        st.write("### Input Text Example:")
        st.code("আমি খুব খারাপ আছি 😢", language="plain")
        st.code("তুমি কেন এমন করলে? 😡", language="plain")
        st.code("তুমি আমাকে রাগিয়ে দিচ্ছ 😠", language="plain")
        st.code("আজকে সবকিছুই বিরক্তিকর 😡", language="plain")
        st.code("আজ আমার খুব মন খারাপ।", language="plain")
        st.code("আমি খুব একা বোধ করছি।", language="plain")
        st.code("জীবনটা কেন এত কঠিন!", language="plain")
        st.code("কিছুই যেন আর ভালো লাগছে না।", language="plain")
        st.code("মনে হচ্ছে সব কিছু ভেঙে পড়ছে।", language="plain")
        st.code("আজ আমি খুব আনন্দিত!", language="plain")
        st.code("এটা আমার জীবনের সেরা মুহূর্ত!", language="plain")
        st.code("সবকিছু এত সুন্দর লাগছে!", language="plain")
        st.code("আজকের দিনটা সত্যিই অসাধারণ!", language="plain")
    # Dataset preview
    df = data_load(file_path)
    st.write("## Dataset Preview")
    st.dataframe(df, height=200)

    # Model performance section
    st.write("## Model Performance")
    if model:
        loss, accuracy = model.evaluate(X_test, y_test)
        st.metric(label="Accuracy", value=f"{accuracy:.2f}")
        st.progress(accuracy)
    else:
        st.error("Error: Model is not initialized properly.")

    # Predict sentiment
    st.write("## Predict Sentiment")
    user_input = st.text_area("Enter Bangla text for prediction", "")
    if st.button("Show Prediction"):
        if user_input:
            predicted_label = predict_sentiment(user_input, model, tokenizer, encoder, max_length)
            st.success(f"**Predicted Sentiment**: {predicted_label}")
        else:
            st.warning("Please enter text for prediction.")

else:
    st.warning("Please log in to use the sentiment analysis tool.")

# Footer section
st.markdown(
    """
    <hr style="border: 1px solid #e74c3c;">
    <div style="text-align:center;">
        <p style="color:yellow;font-weight:bold;">Bangla Sentiment Analysis App | Powered by BanglaNLP</p>
    </div>
    """, 
    unsafe_allow_html=True
)
