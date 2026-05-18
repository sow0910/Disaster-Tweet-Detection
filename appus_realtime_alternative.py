

import streamlit as st
import pandas as pd
import joblib
import folium
import plotly.express as px
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import time
import subprocess
import json
import requests
from bs4 import BeautifulSoup
import random
import sys


# PAGE CONFIG
st.set_page_config(page_title="Urban Risk Dashboard - Alternative Sources", layout="wide")
from streamlit_autorefresh import st_autorefresh

st.title("🌐 Real-Time Risk Monitoring Dashboard - Alternative Sources")
st.caption("Monitors hazard-related posts from multiple social media platforms using AI")

# Check Python version for snscrape compatibility
python_version = sys.version_info
if python_version.major == 3 and python_version.minor >= 13:
    st.sidebar.info("💡 Tip: Use Reddit or RSS for real-time data (works with Python 3.13)")

# Auto-refresh every 5 minutes (disabled for now to prevent data loss)
# st_autorefresh(interval=300000, key="refresh")
# st.info(f"Last updated at: {datetime.now().strftime('%H:%M:%S')} — next refresh in ~5 min")


# INITIALIZE SESSION STATE (to persist data)

if 'df_data' not in st.session_state:
    st.session_state.df_data = pd.DataFrame()
if 'last_fetch_time' not in st.session_state:
    st.session_state.last_fetch_time = None
if 'data_source_used' not in st.session_state:
    st.session_state.data_source_used = None


# LOAD MODEL AND VECTORIZER

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


# DATA SOURCE SELECTION

st.sidebar.header("📡 Data Source Selection")
data_source = st.sidebar.selectbox(
    "Choose data source:",
    [
        "🐦 Twitter (snscrape - No API needed)",
        "📱 Reddit (Free API)",
        "📰 News RSS Feeds",
        "🔄 Simulated Real-Time (from CSV)"
    ]
)

# Clear data if switching data sources
if st.session_state.data_source_used and st.session_state.data_source_used != data_source:
    st.session_state.df_data = pd.DataFrame()
st.session_state.data_source_used = data_source


# HELPER FUNCTIONS

def detect_location(text):
    """Extract location from text"""
    locations = {
        "Delhi": [28.6139, 77.2090],
        "Mumbai": [19.0760, 72.8777],
        "Chennai": [13.0827, 80.2707],
        "Hyderabad": [17.3850, 78.4867],
        "Kolkata": [22.5726, 88.3639],
        "Pune": [18.5204, 73.8567],
        "Bangalore": [12.9716, 77.5946],
        "Bangaluru": [12.9716, 77.5946]
    }
    text_lower = text.lower()
    for city in locations.keys():
        if city.lower() in text_lower:
            return city
    return "Unknown"


# METHOD 1: TWITTER USING SNSCRAPE (No API needed!)

def fetch_tweets_snscrape(query, limit=30):
    """Fetch tweets using snscrape (no API required)"""
    try:
        # Try using snscrape Python library first (more reliable)
        try:
            import snscrape.modules.twitter as sntwitter
            tweets = []
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                if i >= limit:
                    break
                tweets.append({
                    "Date": tweet.date,
                    "Tweet": tweet.rawContent or tweet.content or "",
                    "Location": "Unknown",
                    "Source": "Twitter (snscrape)"
                })
            if tweets:
                return pd.DataFrame(tweets)
        except (ImportError, AttributeError) as e:
            # Python 3.13 compatibility issue - snscrape doesn't work with Python 3.13
            error_str = str(e)
            if "find_module" in error_str or "FileFinder" in error_str:
                st.error("⚠️ snscrape doesn't work with Python 3.13. Use Reddit or RSS Feeds instead.")
                return pd.DataFrame()
            # Fallback to command-line tool
            pass
        except Exception as e:
            st.warning(f"⚠️ Library method failed: {str(e)}. Trying command-line...")
        
        # Fallback to command-line tool
        cmd = [
            "snscrape",
            "--jsonl",
            "--max-results", str(limit),
            f"twitter-search:{query}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and result.stdout:
            data = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        tweet = json.loads(line)
                        content = tweet.get("rawContent") or tweet.get("content") or ""
                        if content:  # Only add if there's actual content
                            data.append({
                                "Date": tweet.get("date", datetime.now()),
                                "Tweet": content,
                                "Location": "Unknown",
                                "Source": "Twitter (snscrape)"
                            })
                    except:
                        continue
            if data:
                return pd.DataFrame(data)
        
        # If we get here, no data was found
        return pd.DataFrame()
        
    except FileNotFoundError:
        st.error("⚠️ snscrape not installed. Try: `pip install snscrape` or `pip install git+https://github.com/JustAnotherArchivist/snscrape.git`")
        return pd.DataFrame()
    except subprocess.TimeoutExpired:
        st.warning("⚠️ Request timed out. Try reducing the limit or simpler query.")
        return pd.DataFrame()
    except Exception as e:
        error_msg = str(e)
        if "find_module" in error_msg or "FileFinder" in error_msg:
            st.error("⚠️ snscrape incompatible with Python 3.13. Use Python 3.11/3.12 or try Reddit/RSS instead.")
        elif "No module named" in error_msg or "snscrape" in error_msg.lower():
            st.error("⚠️ snscrape not installed. Install with: `pip install snscrape`")
        else:
            st.warning(f"⚠️ Error fetching tweets: {error_msg}")
        return pd.DataFrame()

# METHOD 2: REDDIT (Free API, no authentication needed for basic)

def fetch_reddit_posts(subreddit="news", limit=30, keywords=""):
    """Fetch posts from Reddit"""
    try:
        # Clean subreddit name (remove r/ if present)
        subreddit = subreddit.replace("r/", "").replace("/", "").strip()
        if not subreddit:
            return pd.DataFrame()
        
        # Reddit API endpoint (no auth needed for public data)
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={min(limit, 100)}"
        headers = {
            "User-Agent": "UrbanSafetyMonitor/1.0 (Educational Project)"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            posts = []
            
            children = data.get("data", {}).get("children", [])
            if not children:
                return pd.DataFrame()
            
            for post in children:
                post_data = post.get("data", {})
                title = post_data.get("title", "")
                selftext = post_data.get("selftext", "")
                text = f"{title} {selftext}".strip()
                
                if not text:  # Skip empty posts
                    continue
                
                # Filter by keywords if provided
                if keywords and keywords.strip():
                    keyword_list = [kw.strip().lower() for kw in keywords.split() if kw.strip()]
                    if keyword_list:
                        text_lower = text.lower()
                        if not any(kw in text_lower for kw in keyword_list):
                            continue
                
                posts.append({
                    "Date": datetime.fromtimestamp(post_data.get("created_utc", time.time())),
                    "Tweet": text[:500],  # Limit length
                    "Location": "Unknown",
                    "Source": f"Reddit (r/{subreddit})"
                })
            
            if posts:
                return pd.DataFrame(posts)
            else:
                return pd.DataFrame()
        elif response.status_code == 404:
            st.error(f"❌ Subreddit 'r/{subreddit}' not found. Check the name and try again.")
            return pd.DataFrame()
        elif response.status_code == 429:
            st.warning("⚠️ Too many requests to Reddit. Please wait a few minutes and try again.")
            return pd.DataFrame()
        else:
            st.warning(f"⚠️ Reddit API returned status {response.status_code}. Try again later.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ Network error: {str(e)}. Check your internet connection.")
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"⚠️ Error fetching Reddit posts: {str(e)}")
        return pd.DataFrame()


# METHOD 3: RSS FEEDS (News sources)

def fetch_rss_feeds(feed_urls, limit=30):
    """Fetch news from RSS feeds"""
    try:
        all_items = []
        
        for url in feed_urls:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, "xml")
                
                items = soup.find_all("item")[:limit//len(feed_urls)]
                for item in items:
                    title = item.find("title")
                    description = item.find("description")
                    pub_date = item.find("pubDate")
                    
                    text = ""
                    if title:
                        text += title.get_text()
                    if description:
                        text += " " + description.get_text()
                    
                    date_str = pub_date.get_text() if pub_date else datetime.now().isoformat()
                    
                    all_items.append({
                        "Date": date_str,
                        "Tweet": text[:500],
                        "Location": "Unknown",
                        "Source": "RSS Feed"
                    })
            except:
                continue
        
        return pd.DataFrame(all_items)
    except Exception as e:
        st.warning(f"⚠️ Error fetching RSS feeds: {str(e)}")
        return pd.DataFrame()


# METHOD 4: SIMULATED REAL-TIME FROM CSV

def simulate_realtime_from_csv(csv_path, num_posts=30):
    """Simulate real-time posts by randomly sampling from CSV with timestamps"""
    try:
        df = pd.read_csv(csv_path)
        
        # Ensure we have a text column
        text_col = None
        for col in ["Tweet", "text", "Text", "tweet"]:
            if col in df.columns:
                text_col = col
                break
        
        if text_col is None:
            st.error("CSV must contain a 'Tweet' or 'text' column")
            return pd.DataFrame()
        
        # Sample random posts
        sample_df = df.sample(min(num_posts, len(df)))
        
        # Generate recent timestamps
        now = datetime.now()
        data = []
        for idx, row in sample_df.iterrows():
            # Random time in last 24 hours
            random_hours = random.randint(0, 24)
            random_minutes = random.randint(0, 60)
            post_time = now - timedelta(hours=random_hours, minutes=random_minutes)
            
            data.append({
                "Date": post_time,
                "Tweet": str(row[text_col]),
                "Location": row.get("Location", "Unknown"),
                "Source": "Simulated Real-Time"
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        st.warning(f"⚠️ Error reading CSV: {str(e)}")
        return pd.DataFrame()


# MAIN DASHBOARD LOGIC

# Use session state to persist data
df = st.session_state.df_data.copy() if not st.session_state.df_data.empty else pd.DataFrame()

if data_source == "🐦 Twitter (snscrape - No API needed)":
    st.sidebar.subheader("Twitter Settings")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 13:
        st.sidebar.warning("⚠️ Twitter needs Python 3.12. Use Reddit/RSS instead (works now!)")
    else:
        st.sidebar.info("💡 Install: `pip install snscrape`")
    
    query = st.sidebar.text_input(
        "Search query (keywords, hashtags):",
        value="fire OR flood OR earthquake OR accident OR crime",
        help="Examples: 'fire OR flood', '#disaster', 'accident Mumbai'"
    )
    tweet_limit = st.sidebar.slider("Number of tweets:", 10, 100, 30)
    
    if st.sidebar.button("🔍 Fetch Tweets"):
        with st.spinner("Fetching tweets using snscrape (this may take a moment)..."):
            df = fetch_tweets_snscrape(query, tweet_limit)
            if not df.empty:
                st.session_state.df_data = df
                st.session_state.last_fetch_time = datetime.now()
                st.success(f"✅ Fetched {len(df)} tweets!")
            else:
                st.error("❌ No tweets found. Check: 1) snscrape is installed (`pip install snscrape`), 2) Internet connection, 3) Try different keywords (e.g., 'fire', 'flood', 'accident')")

elif data_source == "📱 Reddit (Free API)":
    st.sidebar.subheader("Reddit Settings")
    st.sidebar.markdown("""
    **✅ No Setup Needed!**
    - Reddit API works without authentication
    - Just enter a subreddit name
    - Popular: news, worldnews, india, emergency
    """)
    
    subreddit = st.sidebar.text_input(
        "Subreddit name:", 
        value="news",
        help="Enter without 'r/' prefix. Examples: news, worldnews, india"
    )
    keywords = st.sidebar.text_input(
        "Filter keywords (optional):", 
        value="",
        help="Leave empty to get all posts, or enter keywords separated by spaces"
    )
    post_limit = st.sidebar.slider("Number of posts:", 10, 100, 30)
    
    if st.sidebar.button("🔍 Fetch Reddit Posts"):
        with st.spinner("Fetching Reddit posts..."):
            df = fetch_reddit_posts(subreddit, post_limit, keywords)
            if not df.empty:
                st.session_state.df_data = df
                st.session_state.last_fetch_time = datetime.now()
                st.success(f"✅ Fetched {len(df)} Reddit posts!")
            else:
                if not keywords or keywords.strip() == "":
                    st.warning("⚠️ No posts found. Try: 1) Different subreddit (e.g., 'worldnews', 'india'), 2) Check subreddit name is correct (no 'r/' prefix)")
                else:
                    st.warning("⚠️ No posts found matching keywords. Try: 1) Remove keyword filters, 2) Use broader keywords, 3) Different subreddit")

elif data_source == "📰 News RSS Feeds":
    st.sidebar.subheader("RSS Feed Settings")
    st.sidebar.markdown("""
    **📋 Setup:**
    - Install: `pip install beautifulsoup4 requests`
    - Find RSS feeds on news websites (look for 📡 icon)
    - Paste URLs one per line
    """)
    
    default_feeds = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss",
        "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"
    ]
    
    feed_urls_input = st.sidebar.text_area(
        "RSS Feed URLs (one per line):",
        value="\n".join(default_feeds),
        height=120,
        help="Each URL on a new line. Examples: BBC, CNN, Times of India feeds"
    )
    feed_limit = st.sidebar.slider("Number of articles:", 10, 100, 30)
    
    if st.sidebar.button("🔍 Fetch News Articles"):
        feed_urls = [url.strip() for url in feed_urls_input.split("\n") if url.strip()]
        if not feed_urls:
            st.error("❌ Please enter at least one RSS feed URL")
        else:
            with st.spinner("Fetching news articles..."):
                df = fetch_rss_feeds(feed_urls, feed_limit)
                if not df.empty:
                    st.session_state.df_data = df
                    st.session_state.last_fetch_time = datetime.now()
                    st.success(f"✅ Fetched {len(df)} news articles!")
                else:
                    st.warning("⚠️ No articles found. Check: 1) RSS URLs are valid (test in browser), 2) Internet connection, 3) Try different feeds")

elif data_source == "🔄 Simulated Real-Time (from CSV)":
    st.sidebar.subheader("Simulation Settings")
    st.sidebar.markdown("""
    **✅ No Setup Needed!**
    - Uses your existing CSV file
    - CSV must have: 'Tweet' or 'text' column
    - Optional: 'Location' column
    """)
    
    csv_path = st.sidebar.text_input(
        "CSV file path:",
        value="datasets/sample_tweets - Sheet1.csv",
        help="Path relative to project root. Example: datasets/sample_tweets - Sheet1.csv"
    )
    sim_limit = st.sidebar.slider("Number of posts to simulate:", 5, 50, 20)
    
    if st.sidebar.button("🔄 Start Simulation"):
        with st.spinner("Simulating real-time posts..."):
            df = simulate_realtime_from_csv(csv_path, sim_limit)
            if not df.empty:
                st.session_state.df_data = df
                st.session_state.last_fetch_time = datetime.now()
                st.success(f"✅ Generated {len(df)} simulated posts!")
            else:
                st.error("❌ Error reading CSV. Check: 1) File path is correct, 2) CSV has 'Tweet' or 'text' column")


# PROCESS AND DISPLAY DATA

# Add clear data button
if not st.session_state.df_data.empty:
    if st.sidebar.button("🗑️ Clear Current Data"):
        st.session_state.df_data = pd.DataFrame()
        st.session_state.last_fetch_time = None
        st.rerun()

# Show last fetch time and data status
if not st.session_state.df_data.empty:
    st.sidebar.success(f"✅ {len(st.session_state.df_data)} posts loaded")
    if st.session_state.last_fetch_time:
        st.sidebar.info(f"📅 Last fetched: {st.session_state.last_fetch_time.strftime('%H:%M:%S')}")
else:
    st.sidebar.info("👆 Fetch data using the options above")

if not st.session_state.df_data.empty:
    df = st.session_state.df_data.copy()
    # Add predictions
    X_tfidf = vectorizer.transform(df["Tweet"].astype(str))
    df["Prediction"] = model.predict(X_tfidf)
    df["Risk Label"] = df["Prediction"].apply(lambda x: "🔥 Hazard" if x == 1 else "😊 Safe")
    
    # Detect locations
    df["Location"] = df["Tweet"].apply(detect_location)
    
    # Format dates
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Display data
    st.subheader("📢 Live Hazard Reports")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_only_hazards = st.checkbox("Show only hazards", value=False)
    with col2:
        location_filter = st.selectbox("Filter by location:", ["All"] + list(df["Location"].unique()))
    
    display_df = df.copy()
    if show_only_hazards:
        display_df = display_df[display_df["Risk Label"] == "🔥 Hazard"]
    if location_filter != "All":
        display_df = display_df[display_df["Location"] == location_filter]
    
    st.dataframe(
        display_df[["Date", "Location", "Tweet", "Risk Label", "Source"]],
        use_container_width=True,
        height=400
    )
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Posts", len(df))
    with col2:
        st.metric("🔥 Hazards Detected", len(df[df["Risk Label"] == "🔥 Hazard"]))
    with col3:
        st.metric("😊 Safe Posts", len(df[df["Risk Label"] == "😊 Safe"]))
    with col4:
        hazard_pct = (len(df[df["Risk Label"] == "🔥 Hazard"]) / len(df)) * 100
        st.metric("Hazard Rate", f"{hazard_pct:.1f}%")
    
 
    # SUMMARY CHART
  
    st.subheader("📊 Risk Summary")
    summary = df["Risk Label"].value_counts().reset_index()
    summary.columns = ["Risk Level", "Count"]
    fig = px.bar(
        summary,
        x="Risk Level",
        y="Count",
        color="Risk Level",
        text="Count",
        title="Distribution of Hazard Posts"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Source breakdown
    if "Source" in df.columns:
        st.subheader("📡 Data Source Breakdown")
        source_summary = df.groupby(["Source", "Risk Label"]).size().reset_index(name="Count")
        fig2 = px.bar(
            source_summary,
            x="Source",
            y="Count",
            color="Risk Label",
            title="Posts by Source and Risk Level"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
  
    # MAP VISUALIZATION
  
    st.subheader("🗺️ Real-Time Risk Map")
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    
    city_coords = {
        "Delhi": [28.6139, 77.2090],
        "Mumbai": [19.0760, 72.8777],
        "Chennai": [13.0827, 80.2707],
        "Hyderabad": [17.3850, 78.4867],
        "Kolkata": [22.5726, 88.3639],
        "Pune": [18.5204, 73.8567],
        "Bangalore": [12.9716, 77.5946],
        "Bangaluru": [12.9716, 77.5946]
    }
    
    hazard_count = 0
    safe_count = 0
    
    for _, row in df.iterrows():
        if row["Location"] in city_coords:
            color = "red" if row["Risk Label"] == "🔥 Hazard" else "green"
            
            if row["Risk Label"] == "🔥 Hazard":
                hazard_count += 1
            else:
                safe_count += 1
            
            folium.Marker(
                location=city_coords[row["Location"]],
                popup=f"""
                <b>{row['Location']}</b><br>
                {row['Risk Label']}<br>
                <small>{row['Tweet'][:100]}...</small><br>
                <small>Source: {row.get('Source', 'Unknown')}</small>
                """,
                icon=folium.Icon(color=color)
            ).add_to(m)
    
    st_folium(m, width=700, height=400)
    
    # Download results
    st.download_button(
        "📥 Download Results CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"hazard_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    st.success(f"✅ Dashboard updated at {datetime.now().strftime('%H:%M:%S')}")
    
else:
    st.info("👆 Select a data source and click the fetch button to begin monitoring.")

# FOOTER

st.markdown("---")
with st.expander("📖 Setup Instructions & Help"):
    st.markdown("""
    ### Quick Setup Guide:
    
    **🐦 Twitter (snscrape):**
    - Install: `pip install snscrape`
    - Or: `pip install git+https://github.com/JustAnotherArchivist/snscrape.git`
    - Verify: `snscrape --version`
    
    **📱 Reddit:**
    - ✅ No setup needed! Works immediately
    - Just enter subreddit name (e.g., `news`, `worldnews`, `india`)
    
    **📰 RSS Feeds:**
    - Install: `pip install beautifulsoup4 requests`
    - Find RSS feeds on news websites
    - Paste URLs (one per line)
    
    **🔄 CSV Simulation:**
    - ✅ No setup needed!
    - Uses your existing CSV file
    
    ### 📚 For detailed instructions, see: `DATA_SOURCES_GUIDE.md`
    """)
    
st.markdown("""
### 💡 Tips:
- **Start with Reddit** - Easiest to use, no setup required
- **RSS Feeds** - Most reliable for news articles
- **CSV Simulation** - Best for testing your model
- **Twitter (snscrape)** - Most comprehensive but requires installation
""")

