# 📡 Data Sources Setup Guide

This guide explains how to set up and use each data source in `appus_realtime_alternative.py`.

---

## 🐦 Method 1: Twitter using snscrape (No API Keys Needed!)

### Step 1: Install snscrape
```bash
pip install snscrape
```

**Note:** On some systems, you might need to install it differently:
```bash
# If the above doesn't work, try:
pip install git+https://github.com/JustAnotherArchivist/snscrape.git
```

### Step 2: Verify Installation
```bash
snscrape --version
```

### Step 3: Use in the App
1. Run the Streamlit app: `streamlit run appus_realtime_alternative.py`
2. Select **"🐦 Twitter (snscrape - No API needed)"** from the sidebar
3. Enter your search query (examples):
   - `fire OR flood OR earthquake`
   - `#disaster OR #emergency`
   - `accident Mumbai`
   - `flood warning India`
4. Set the number of tweets (10-100)
5. Click **"🔍 Fetch Tweets"**

### Example Queries:
- `fire OR flood OR earthquake OR accident OR crime`
- `disaster India`
- `#flood #fire #earthquake`
- `emergency Delhi OR Mumbai`

### Troubleshooting:
- **Error: "snscrape not found"** → Make sure snscrape is installed and in your PATH
- **Timeout errors** → Reduce the number of tweets or try a simpler query
- **No results** → Try different keywords or check your internet connection

---

## 📱 Method 2: Reddit (Free API - No Authentication!)

### Step 1: No Installation Needed!
Reddit's public API works without any authentication. Just make sure `requests` is installed:
```bash
pip install requests
```

### Step 2: Use in the App
1. Run the Streamlit app: `streamlit run appus_realtime_alternative.py`
2. Select **"📱 Reddit (Free API)"** from the sidebar
3. Enter a subreddit name (examples):
   - `news` - General news
   - `worldnews` - World news
   - `india` - India-specific news
   - `disaster` - Disaster-related posts
   - `emergency` - Emergency situations
4. (Optional) Enter keywords to filter: `fire flood accident disaster`
5. Set the number of posts (10-100)
6. Click **"🔍 Fetch Reddit Posts"**

### Popular Subreddits for Disaster Monitoring:
- `r/news` - General news
- `r/worldnews` - International news
- `r/india` - India-specific news
- `r/emergency` - Emergency situations
- `r/disaster` - Disaster-related content
- `r/PublicSafety` - Public safety alerts

### Example Setup:
- **Subreddit:** `news`
- **Keywords:** `fire flood accident disaster emergency`
- **Limit:** 30 posts

### Troubleshooting:
- **429 Error (Too Many Requests)** → Wait a few minutes and try again
- **No posts found** → Try a different subreddit or remove keyword filters
- **Connection error** → Check your internet connection

---

## 📰 Method 3: RSS Feeds (News Sources)

### Step 1: Install Required Library
```bash
pip install beautifulsoup4 requests
```

### Step 2: Find RSS Feed URLs
You can use any RSS feed URL. Here are some popular ones:

**International News:**
- BBC News: `https://feeds.bbci.co.uk/news/rss.xml`
- CNN: `https://rss.cnn.com/rss/edition.rss`
- Reuters: `https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best`
- The Guardian: `https://www.theguardian.com/world/rss`

**India-Specific News:**
- Times of India: `https://timesofindia.indiatimes.com/rssfeeds/296589292.cms`
- Hindustan Times: `https://www.hindustantimes.com/rss/topnews/rssfeed.xml`
- The Hindu: `https://www.thehindu.com/news/national/feeder/default.rss`
- India Today: `https://www.indiatoday.in/rss/1206577`

**Disaster/Emergency Feeds:**
- Google News (India): `https://news.google.com/rss/search?q=disaster+india&hl=en-IN&gl=IN&ceid=IN:en`
- Google News (Emergency): `https://news.google.com/rss/search?q=emergency+OR+disaster+OR+fire+OR+flood&hl=en&gl=US&ceid=US:en`

### Step 3: Use in the App
1. Run the Streamlit app: `streamlit run appus_realtime_alternative.py`
2. Select **"📰 News RSS Feeds"** from the sidebar
3. Enter RSS feed URLs (one per line) in the text area
4. Set the number of articles (10-100)
5. Click **"🔍 Fetch News Articles"**

### Example RSS Feed Setup:
```
https://feeds.bbci.co.uk/news/rss.xml
https://timesofindia.indiatimes.com/rssfeeds/296589292.cms
https://news.google.com/rss/search?q=disaster+india&hl=en-IN&gl=IN&ceid=IN:en
```

### How to Find RSS Feeds:
1. Visit a news website
2. Look for an RSS icon (📡) or "RSS" link
3. Right-click and "Copy link address"
4. Paste it into the app

### Troubleshooting:
- **No articles found** → Check if the RSS feed URL is valid (try opening it in a browser)
- **Connection timeout** → Some feeds may be slow, try others
- **Invalid XML** → The feed might be malformed, try a different source

---

## 🔄 Method 4: Simulated Real-Time (from CSV)

### Step 1: Prepare Your CSV File
Your CSV should have a column named:
- `Tweet` or `text` or `Text` or `tweet`

Optional columns:
- `Location` - for location detection

### Step 2: Use in the App
1. Run the Streamlit app: `streamlit run appus_realtime_alternative.py`
2. Select **"🔄 Simulated Real-Time (from CSV)"** from the sidebar
3. Enter the path to your CSV file (e.g., `datasets/sample_tweets - Sheet1.csv`)
4. Set the number of posts to simulate (5-50)
5. Click **"🔄 Start Simulation"**

The app will:
- Randomly sample posts from your CSV
- Assign random timestamps (within last 24 hours)
- Process them through your ML model
- Display as if they were real-time posts

---

## 🚀 Quick Start Checklist

### For Twitter (snscrape):
- [ ] Install snscrape: `pip install snscrape`
- [ ] Verify: `snscrape --version`
- [ ] Run app and select Twitter option
- [ ] Enter search query
- [ ] Click "Fetch Tweets"

### For Reddit:
- [ ] Ensure `requests` is installed: `pip install requests`
- [ ] Run app and select Reddit option
- [ ] Enter subreddit name (e.g., `news`)
- [ ] (Optional) Add keywords
- [ ] Click "Fetch Reddit Posts"

### For RSS Feeds:
- [ ] Install: `pip install beautifulsoup4 requests`
- [ ] Find RSS feed URLs
- [ ] Run app and select RSS Feeds option
- [ ] Paste RSS URLs (one per line)
- [ ] Click "Fetch News Articles"

---

## 💡 Tips & Best Practices

1. **Start Small**: Begin with 10-20 posts to test, then increase
2. **Use Specific Keywords**: More specific queries yield better results
3. **Combine Sources**: Try different sources to get comprehensive coverage
4. **Monitor Rate Limits**: Reddit has rate limits; if you get 429 errors, wait a few minutes
5. **Test RSS Feeds**: Verify RSS URLs work in a browser before using them
6. **Backup Plan**: Always have the CSV simulation as a fallback for testing

---

## ❓ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| snscrape not found | Install: `pip install snscrape` or `pip install git+https://github.com/JustAnotherArchivist/snscrape.git` |
| Reddit 429 error | Wait 5-10 minutes, Reddit limits requests |
| RSS feed not working | Verify URL in browser, try different feed |
| No results found | Try different keywords, check internet connection |
| Timeout errors | Reduce number of posts/limit |

---

## 📞 Need Help?

If you encounter issues:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify your internet connection
3. Try the CSV simulation method first to test your model
4. Check the error messages in the Streamlit app for specific guidance

