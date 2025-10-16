ignore_phrases = [
    "i am a bot",
    "this action was performed automatically",
    "automod",
]

def filter(comments):
    filtered = []

    for c in comments:
        if c["kind"] == "t1":
            author = c["data"].get("author", "")
            body = c["data"].get("body", "").strip()

            if (
                len(body) > 20 and
                not author.lower().endswith("bot") and
                all(phrase not in body.lower() for phrase in ignore_phrases)
            ):
                filtered.append(body)

    return filtered

def run_sentiment_analysis(comments, sentiment_model):
    results = []
    for text in comments:
        res = sentiment_model(text)[0]
        results.append({
            "text": text,
            "label": res["label"],
            "score": res["score"]
        })

    return results

def summarise_analysed_posts(analysed, top_n=10):
    total = len(analysed)
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    grouped = {"POSITIVE": [], "NEGATIVE": [], "NEUTRAL": []}

    for r in analysed:
        label = r.get("label", "NEUTRAL").upper()
        if label not in grouped:
            label = "NEUTRAL"
        grouped[label].append(r)

        if label == "POSITIVE":
            counts["positive"] += 1
        elif label == "NEGATIVE":
            counts["negative"] += 1
        else:
            counts["neutral"] += 1

    avg_sentiment = (counts["positive"] - counts["negative"]) / total if total else 0

    if avg_sentiment > 0.3:
        vibe = "positive"
    elif avg_sentiment < -0.3:
        vibe = "negative"
    else:
        vibe = "neutral"

    relevant_comments = []
    
    for label, group in grouped.items():
        if not group:
            continue
        n_comments = round(top_n * len(group) / total)
        top_comments = sorted(group, key=lambda x: x["score"], reverse=True)[:n_comments]
        relevant_comments.extend([c["text"] for c in top_comments])

    if len(relevant_comments) < top_n:
        top_overall = sorted(analysed, key=lambda x: x["score"], reverse=True)
        for c in top_overall:
            if c["text"] not in relevant_comments:
                relevant_comments.append(c["text"])
            if len(relevant_comments) == top_n:
                break

    return {
        "vibe": vibe,
        "avg_sentiment": round(avg_sentiment, 2),
        "posts_analyzed": total,
        "breakdown": counts,
        "relevant_comments": relevant_comments,
    }
