from sentence_transformers import SentenceTransformer, util
from itertools import chain
from datetime import datetime

embedder = SentenceTransformer("all-MiniLM-L6-v2")

IGNORE_PHRASES = {
    "i am a bot",
    "this action was performed automatically",
    "automod",
}

def filter_comments(comments):
    """Filter out bot/automod comments and very short entries."""
    def is_valid(c):
        if c.get("kind") != "t1":
            return False

        data = c.get("data", {})
        author = data.get("author", "").lower()
        body = data.get("body", "").strip()

        if len(body) < 20 or author.endswith("bot"):
            return False
        body_l = body.lower()
        return not any(p in body_l for p in IGNORE_PHRASES)

    return [c["data"]["body"].strip() for c in comments if is_valid(c)]

def get_relevant_comments(comments, topic, threshold=0.10):
    topic_embedding = embedder.encode(topic, convert_to_tensor=True)
    filtered = []

    for c in comments:
        body = c.lower()
        comment_embedding = embedder.encode(body, convert_to_tensor=True)
        similarity = util.cos_sim(topic_embedding, comment_embedding).item()
        if similarity > threshold:
            filtered.append(c)

    return filtered

def run_sentiment_analysis(comments, sentiment_model):
    """Run sentiment analysis on a list of text strings."""
    return [
        {
            "text": text,
            "label": (res := sentiment_model(text)[0])["label"].upper(),
            "score": res["score"],
        }
        for text in comments
    ]


def summarise_analysed_posts(analysed, topic, top_n=10):
    """Summarise analysed sentiment results into one vibe score."""
    if not analysed:
        return {
            "vibe": "neutral",
            "avg_sentiment": 0.0,
            "posts_analyzed": 0,
            "breakdown": {"positive": 0, "negative": 0, "neutral": 0},
            "relevant_comments": [],
        }

    grouped = {"POSITIVE": [], "NEGATIVE": [], "NEUTRAL": []}
    for r in analysed:
        label = grouped.get(r["label"].upper(), grouped["NEUTRAL"])
        label.append(r)

    counts = {k.lower(): len(v) for k, v in grouped.items()}
    total = len(analysed)

    avg_sentiment = (counts["positive"] - counts["negative"]) / total
    vibe = (
        "positive" if avg_sentiment > 0.3
        else "negative" if avg_sentiment < -0.3
        else "neutral"
    )

    proportions = {
        label: max(1, round(top_n * len(group) / total))
        for label, group in grouped.items() if group
    }

    comments = list(
        chain.from_iterable(
            [
                c["text"]
                for c in sorted(group, key=lambda x: x["score"], reverse=True)[:n]
            ]
            for label, group in grouped.items()
            if (n := proportions.get(label))
        )
    )

    if len(comments) < top_n:
        for c in sorted(analysed, key=lambda x: x["score"], reverse=True):
            if c["text"] not in comments:
                comments.append(c["text"])
            if len(comments) >= top_n:
                break

    relevant_comments = get_relevant_comments(comments, topic)

    return {
        "avg_sentiment": round(avg_sentiment, 2),
        "breakdown": counts,
        "posts_analyzed": total,
        "relevant_comments": relevant_comments,
        "timestamp": datetime.now().isoformat(),
        "vibe": vibe,
    }
