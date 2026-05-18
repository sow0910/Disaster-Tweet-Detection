# ===================================================
# 🌍 Real-Time Urban Safety Hazard Monitoring Dashboard
# ===================================================

import streamlit as st
import pandas as pd
import tweepy
import joblib
import folium
import plotly.express as px
from streamlit_folium import st_folium


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Urban Risk Dashboard", layout="wide")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=600000, key="refresh")
import streamlit as st
from datetime import datetime


st.info(f"Last updated at: {datetime.now().strftime('%H:%M:%S')} — next refresh in ~10 min")

st.title("🌐 Real-Time Risk Monitoring Dashboard for Urban Safety Hazards")
st.caption("Automatically detects and maps hazard-related tweets using AI")

# ---------------------------------------------------
# LOAD MODEL AND VECTORIZER
# ---------------------------------------------------
@st.cache_resource
def load_model():
    model = joblib.load("tweet_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer

try:
    model, vectorizer = load_model()
    st.sidebar.success("✅ Model Loaded Successfully")
except:
    st.sidebar.error("⚠️ Model or vectorizer file missing.")
    st.stop()

# ---------------------------------------------------
# TWITTER API CONFIG
# ---------------------------------------------------
st.sidebar.header("🧠 Twitter Connection")
bearer = st.sidebar.text_input("Enter your Twitter/X Bearer Token:", type="password")

query = st.sidebar.text_input("Enter keywords / hashtags to monitor:",
                              "#fire OR #flood OR #earthquake OR #crime OR #accident")
tweet_limit = st.sidebar.slider("Number of recent tweets to fetch:", 10, 100, 30)

# ---------------------------------------------------
# FETCH TWEETS
# ---------------------------------------------------
import pandas as pd
import tweepy
import streamlit as st

def fetch_tweets(query, bearer, tweet_limit=50):
    """Fetch tweets or load sample fallback."""
    try:
        client = tweepy.Client(bearer_token=bearer)
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(tweet_limit, 100),
            tweet_fields=["created_at", "text", "geo", "lang"]
        )

        data = []
        if tweets.data:
            for t in tweets.data:
                data.append({
                    "Date": t.created_at,
                    "Tweet": t.text,
                    "Location": "Unknown"
                })
            return pd.DataFrame(data)

        else:
            st.warning("⚠️ No live tweets found. Showing sample dataset instead.")
            return pd.read_csv("datasets/sample_tweets - Sheet1.csv")

    except Exception as e:
        st.warning("⚠️ Live API unavailable or rate-limited. Showing sample dataset instead.")
        return pd.read_csv("datasets/sample_tweets - Sheet1.csv")


# ---------------------------------------------------
# SIMPLE LOCATION DETECTION (Mock Extraction)
# ---------------------------------------------------
def detect_location(text):
    locations = ["Delhi", "Mumbai", "Chennai", "Hyderabad", "Kolkata", "Pune", "Bangalore"]
    for city in locations:
        if city.lower() in text.lower():
            return city
    return "Unknown"

# ---------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------
if bearer:
    st.info("Fetching live tweets...")
    df = fetch_tweets(query, bearer, tweet_limit)

    if not df.empty:
        # Add prediction
        X_tfidf = vectorizer.transform(df["Tweet"])
        df["Prediction"] = model.predict(X_tfidf)
        df["Risk Label"] = df["Prediction"].apply(lambda x: "🔥 Hazard" if x == 1 else "😊 Safe")
        df["Location"] = df["Tweet"].apply(detect_location)
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        # Display data
        st.subheader("📢 Live Hazard Reports")
        st.dataframe(df[["Date", "Location", "Tweet", "Risk Label"]], use_container_width=True)

        # ---------------------------------------------------
        # SUMMARY CHART
        # ---------------------------------------------------
        st.subheader("📊 Risk Summary")
        summary = df["Risk Label"].value_counts().reset_index()
        summary.columns = ["Risk Level", "Count"]
        fig = px.bar(summary, x="Risk Level", y="Count", color="Risk Level",
                     text="Count", title="Distribution of Hazard Tweets")
        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------
        # MAP VISUALIZATION
        # ---------------------------------------------------
        st.subheader("🗺️ Real-Time Risk Map")
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        city_coords = {
            "Delhi": [28.6139, 77.2090],
            "Mumbai": [19.0760, 72.8777],
            "Chennai": [13.0827, 80.2707],
            "Hyderabad": [17.3850, 78.4867],
            "Kolkata": [22.5726, 88.3639],
            "Pune": [18.5204, 73.8567],
            "Bangalore": [12.9716, 77.5946]
        }

        for _, row in df.iterrows():
            if row["Location"] in city_coords:
                color = "red" if row["Risk Label"] == "🔥 Hazard" else "green"
                folium.Marker(
                    location=city_coords[row["Location"]],
                    popup=f"{row['Location']} — {row['Risk Label']}<br>{row['Tweet'][:80]}...",
                    icon=folium.Icon(color=color)
                ).add_to(m)

        st_folium(m, width=700, height=400)
        st.success(f"✅ Dashboard updated at {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.warning("No tweets found. Try different hashtags or increase limit.")
else:
    st.info("🔑 Please enter your Twitter Bearer Token in the sidebar to begin.")
