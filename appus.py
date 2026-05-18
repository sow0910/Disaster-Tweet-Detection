# ==================================================
# 🧭 Real-Time Risk Monitoring Dashboard
# With ML Model Integration
# ==================================================
import tweepy
import os
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(page_title="Urban Safety Risk Dashboard", layout="wide")
st.title("🧭 Real-Time Risk Monitoring Dashboard for Urban Safety Hazards")
st.write("Detects and classifies tweets related to **crimes, fires, floods, or unsafe zones** using your ML model.")

# --------------------------------------------------
# LOAD MODEL AND VECTORIZER
# --------------------------------------------------
@st.cache_resource
def load_model():
    model = joblib.load("tweet_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

try:
    model, vectorizer = load_model()
    st.sidebar.success("✅ Model & Vectorizer Loaded Successfully!")
except Exception as e:
    st.sidebar.error("⚠️ Could not load model/vectorizer. Please ensure both files exist.")
    st.stop()

# --------------------------------------------------
# SIDEBAR INPUT OPTIONS
# --------------------------------------------------
st.sidebar.header("📂 Data Input Options")
option = st.sidebar.radio("Choose an option:",
                          ("🔹 Enter Tweet Manually",
                           "🔹 Upload CSV Dataset"))

# --------------------------------------------------
# OPTION 1: MANUAL INPUT
# --------------------------------------------------
if option == "🔹 Enter Tweet Manually":
    st.subheader("✏️ Manual Tweet Classification")

    user_tweet = st.text_area("Enter tweet text:")
    if st.button("Predict"):
        if user_tweet.strip() == "":
            st.warning("Please enter some text to analyze.")
        else:
            X_tfidf = vectorizer.transform([user_tweet])
            prediction = model.predict(X_tfidf)[0]
            label = "🔥 Disaster / Risk Tweet" if prediction == 1 else "😊 Not a Disaster Tweet"

            st.success(f"**Prediction:** {label}")

# --------------------------------------------------
# OPTION 2: UPLOAD CSV FILE
# --------------------------------------------------
elif option == "🔹 Upload CSV Dataset":
    st.subheader("📁 Upload Dataset for Bulk Prediction")

    uploaded_file = st.file_uploader("Upload a CSV file containing tweets (column name: text)", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if "text" not in df.columns:
            st.error("CSV must contain a column named 'text'.")
        else:
            st.write("✅ File Uploaded Successfully!")
            df["clean_text"] = df["text"].astype(str)

            # Predict using ML model
            X_tfidf = vectorizer.transform(df["clean_text"])
            df["Prediction"] = model.predict(X_tfidf)
            df["Risk Label"] = df["Prediction"].apply(lambda x: "🔥 Disaster" if x == 1 else "😊 Not Disaster")

            st.dataframe(df[["text", "Risk Label"]], use_container_width=True)

            # --------------------------------------------------
            # SUMMARY CHART
            # --------------------------------------------------
            st.subheader("📊 Risk Level Summary")
            summary = df["Risk Label"].value_counts().reset_index()
            summary.columns = ["Risk Level", "Count"]

            fig = px.bar(summary, x="Risk Level", y="Count",
                         color="Risk Level",
                         title="Distribution of Risk Levels",
                         text="Count")
            st.plotly_chart(fig, use_container_width=True)

            # --------------------------------------------------
            # MAP VISUALIZATION (Optional for now)
            # --------------------------------------------------
            st.subheader("🗺️ Example Risk Zones (Demo Map)")
            m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
            folium.Marker([28.61, 77.20], popup="Delhi - High Alert (Fire)").add_to(m)
            folium.Marker([19.07, 72.87], popup="Mumbai - Flood Warning").add_to(m)
            st_folium(m, width=700, height=400)

            # Download predictions
            st.download_button("📥 Download Results CSV",
                               data=df.to_csv(index=False).encode('utf-8'),
                               file_name="tweet_predictions.csv",
                               mime="text/csv")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown("**Developed by:** Your Team | **Powered by:** Streamlit + Logistic Regression Model")
