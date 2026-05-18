# Disaster Tweet Detection

Real-time disaster-related text classification system using NLP, TF-IDF, Logistic Regression, and Streamlit.

---

## Overview

This project detects whether social media/news text is related to a real disaster or not.

The system processes text from multiple sources such as:

* Reddit feeds
* RSS news feeds
* CSV-based simulated real-time streams

The text is classified as:

* Hazard (Disaster-related)
* Safe (Non-disaster)

The project also includes a Streamlit dashboard for live monitoring, metrics, charts, and map visualization.

---

## Features

* Real-time disaster text classification
* TF-IDF + Logistic Regression NLP pipeline
* Streamlit dashboard
* Reddit and RSS feed integration
* Simulated real-time streaming using CSV
* Interactive charts and metrics
* Map visualization using Folium
* CSV export support

---

## Project Structure

```bash
Disaster-Tweet-Detection/
│
├── appus.py
├── appus_realtime.py
├── appus_realtime_alternative.py
├── tweet_model.pkl
├── vectorizer.pkl
├── train.csv
├── test.csv
├── sample_tweets.csv
├── requirements.txt
├── README.md
├── PROJECT_EXPLANATION.md
└── DATA_SOURCES_GUIDE.md
```

---

## Machine Learning Pipeline

```text
Raw Text
   ↓
Text Cleaning
   ↓
TF-IDF Vectorization
   ↓
Logistic Regression
   ↓
Hazard / Safe Prediction
```

---

## Dataset

Dataset used:

* Kaggle Disaster Tweets Dataset

Files:

* train.csv → training dataset
* test.csv → testing dataset
* sample_tweets.csv → simulated real-time demo data

---

## Model Details

* Algorithm: Logistic Regression
* Feature Extraction: TF-IDF Vectorizer
* Hyperparameter Tuning: GridSearchCV

Evaluation Metrics:

* Accuracy: ~89%
* ROC-AUC: ~0.82

---

## Technologies Used

* Python
* pandas
* scikit-learn
* Streamlit
* Plotly
* Folium
* requests
* BeautifulSoup

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run Application

Main application:

```bash
streamlit run appus_realtime_alternative.py
```

Basic classifier:

```bash
streamlit run appus.py
```

Twitter API version:

```bash
streamlit run appus_realtime.py
```

---

## Demo Flow

1. Select data source
2. Fetch posts/news
3. Model predicts Hazard or Safe
4. Dashboard updates metrics and charts
5. Download results as CSV

---

## Limitations

* Sarcasm and figurative language handling is limited
* Model trained mainly on Twitter-style text
* Location detection is keyword-based
* Twitter API and scraping reliability issues

---

## Future Improvements

* BERT / Transformer models
* Named Entity Recognition (NER)
* FastAPI backend
* Database integration
* Model monitoring and retraining pipeline

---

## Author

Sowndarya
