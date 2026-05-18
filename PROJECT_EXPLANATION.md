# 📚 Project Explanation: Disaster Tweet Detection

## 🤖 MODELS USED IN THE PROJECT

### 1. **TF-IDF Vectorizer (Text Preprocessing Model)**
- **File:** `vectorizer.pkl`
- **What it does:** Converts text (tweets/posts) into numbers that the computer can understand
- **How it works:** 
  - Takes each tweet and breaks it into words
  - Counts how important each word is (words that appear often in disaster tweets get higher scores)
  - Converts the text into a list of numbers (called "features")
- **Example:** 
  - Tweet: "Fire breaks out in Delhi"
  - After TF-IDF: [0.5, 0.8, 0.2, 0.9, 0.1] (numbers representing word importance)

### 2. **Classification Model (Main ML Model)**
- **File:** `tweet_model.pkl`
- **What it does:** Predicts if a tweet is about a disaster (1) or not a disaster (0)
- **Type:** Based on the code structure, it's likely one of these:
  - **Logistic Regression** (most common for text classification)
  - **Naive Bayes** (good for text classification)
  - **Support Vector Machine (SVM)** (good for binary classification)
- **How it works:**
  1. Takes the numbers from TF-IDF vectorizer
  2. Uses patterns it learned from training data
  3. Outputs: 1 = Disaster/Hazard, 0 = Safe/Not Disaster
- **Training:** The model was trained on 8,562 labeled tweets to learn patterns

### 3. **How They Work Together:**
```
Tweet Text → TF-IDF Vectorizer → Numbers → ML Model → Prediction (0 or 1)
```

**In the code:**
```python
# Step 1: Convert text to numbers
X_tfidf = vectorizer.transform(df["Tweet"])

# Step 2: Predict using the model
df["Prediction"] = model.predict(X_tfidf)

# Step 3: Convert to labels
df["Risk Label"] = df["Prediction"].apply(lambda x: "🔥 Hazard" if x == 1 else "😊 Safe")
```

---

## 📊 DATASETS USED IN THE PROJECT

### 1. **train.csv (Training Dataset)**
- **Size:** 8,562 rows (tweets)
- **Columns:**
  - `id`: Unique number for each tweet
  - `keyword`: Optional keyword (often empty)
  - `location`: Optional location (often empty)
  - `text`: The actual tweet text
  - `target`: Label (0 = Not Disaster, 1 = Disaster)
- **Purpose:** Used to train the ML model
- **Example:**
  ```
  id: 1
  text: "Our Deeds are the Reason of this #earthquake May ALLAH Forgive us all"
  target: 1 (Disaster)
  ```

### 2. **test.csv (Testing Dataset)**
- **Size:** 3,700 rows (tweets)
- **Columns:**
  - `id`: Unique number for each tweet
  - `keyword`: Optional keyword
  - `location`: Optional location
  - `text`: The actual tweet text
  - **NO `target` column** (this is what we predict)
- **Purpose:** Used to test the model's accuracy (predictions are made on this)
- **Example:**
  ```
  id: 0
  text: "Just happened a terrible car crash"
  (target is missing - model predicts this)
  ```

### 3. **sample_tweets - Sheet1.csv (Sample Data)**
- **Size:** 7 rows
- **Columns:**
  - `Date`: Date and time of the tweet
  - `Tweet`: The tweet text
  - `Location`: City name (Delhi, Mumbai, Chennai, etc.)
- **Purpose:** Used for testing/demo purposes when real-time data isn't available
- **Example:**
  ```
  Date: 2025-11-11 10:10:00
  Tweet: "Massive fire breaks out in Delhi market"
  Location: Delhi
  ```

### 4. **sample_submission.csv (Submission Format)**
- **Purpose:** Shows the format for submitting predictions
- **Format:** id, target (0 or 1)

---

## 🔄 HOW THE PROJECT WORKS

### **Training Phase (Already Done):**
1. Load `train.csv` with 8,562 labeled tweets
2. Clean and preprocess the text
3. Convert text to numbers using TF-IDF
4. Train the ML model to learn patterns:
   - Words like "fire", "flood", "earthquake" → Disaster (1)
   - Words like "nice", "happy", "sunny" → Not Disaster (0)
5. Save the trained model as `tweet_model.pkl`
6. Save the vectorizer as `vectorizer.pkl`

### **Prediction Phase (What the App Does):**
1. **Get Real-Time Data:**
   - Fetch tweets from Twitter (snscrape)
   - Fetch posts from Reddit
   - Fetch articles from RSS feeds
   - Or use sample CSV data

2. **Process Each Post:**
   - Extract the text
   - Convert to numbers using TF-IDF vectorizer
   - Predict using the trained model
   - Label as "🔥 Hazard" or "😊 Safe"

3. **Display Results:**
   - Show predictions in a table
   - Create charts showing hazard distribution
   - Map locations on a map
   - Allow downloading results

---

## 📈 MODEL PERFORMANCE

The model was trained to recognize:
- **Disaster indicators:** fire, flood, earthquake, accident, crash, emergency, evacuation, etc.
- **Safe indicators:** normal conversation, weather updates (non-disaster), general topics, etc.

**Accuracy:** The model's accuracy depends on how well it was trained. Typically, such models achieve 75-85% accuracy on disaster detection tasks.

---

## 🎯 KEY FEATURES

1. **Real-Time Monitoring:** Fetches live data from social media
2. **Automatic Classification:** Uses AI to classify posts as disaster or safe
3. **Location Detection:** Extracts city names from text
4. **Visualization:** Shows results on maps and charts
5. **Multiple Data Sources:** Twitter, Reddit, RSS feeds, or CSV

---

## 💡 SIMPLE SUMMARY

**What the project does:**
- Takes text from social media (tweets, Reddit posts, news)
- Uses a trained AI model to check if it's about a disaster
- Shows results on a dashboard with maps and charts

**The model:**
- Was trained on 8,562 labeled tweets
- Learned to recognize disaster-related words
- Can predict if new text is about a disaster or not

**The datasets:**
- `train.csv`: 8,562 tweets used for training (with labels)
- `test.csv`: 3,700 tweets for testing (without labels)
- `sample_tweets.csv`: 7 sample tweets for demo/testing

