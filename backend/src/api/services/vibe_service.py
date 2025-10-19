from transformers import pipeline
import requests
from decouple import config
from .vibe_service_utils import filter_comments, run_sentiment_analysis, summarise_analysed_posts

_sentiment_model = None

REDDIT_CLIENT_ID = config("REDDIT_CLIENT_ID")
REDDIT_SECRET = config("REDDIT_SECRET")
USER_AGENT = config("USER_AGENT")

REDDIT_TOKEN_PATH = "https://www.reddit.com/api/v1/access_token"
REDDIT_SEARCH_PATH = "https://oauth.reddit.com/search"
REDDIT_COMMENTS_PATH = "https://oauth.reddit.com/comments/"

def get_model():
    global _sentiment_model

    if _sentiment_model is None:
        _sentiment_model = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            truncation=True
        )

    return _sentiment_model

def get_reddit_token():
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
    data = {"grant_type": "client_credentials"}
    headers = {"User-Agent": USER_AGENT}

    res = requests.post(REDDIT_TOKEN_PATH, auth=auth, data=data, headers=headers)
    res.raise_for_status()

    return res.json()["access_token"]

def fetch_reddit_posts(topic, limit_posts=10, limit_comments=20):
    token = get_reddit_token()
    headers = {"Authorization": f"bearer {token}", "User-Agent": USER_AGENT}

    search_params = {"q": topic, "limit": limit_posts, "sort": "relevance", "type": "link"}
    res = requests.get(REDDIT_SEARCH_PATH, headers=headers, params=search_params)
    res.raise_for_status()
    posts_data = res.json().get("data", {}).get("children", [])

    all_comments = []

    for post in posts_data:
        post_id = post["data"]["id"]
        comments_url = f"{REDDIT_COMMENTS_PATH}{post_id}"
        res = requests.get(comments_url, headers=headers, params={"limit": limit_comments})
        res.raise_for_status()
        post_comments = res.json()[1].get("data", {}).get("children", [])

        all_comments.extend(post_comments) 

    return filter_comments(all_comments)

def analyze_posts(posts):
    sentiment_model = get_model()
    return run_sentiment_analysis(posts, sentiment_model)

def summarise_vibes(analysed, top_n=10):
    return summarise_analysed_posts(analysed, top_n)
