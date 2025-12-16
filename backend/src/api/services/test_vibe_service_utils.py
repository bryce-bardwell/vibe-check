import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from api.services import vibe_service_utils as utils

def test_filter_comments_filters_out_invalid():
    comments = [
        {"kind": "t1", "data": {"author": "bot123", "body": "nice post"}},
        {"kind": "t1", "data": {"author": "user1", "body": "Too short"}},
        {"kind": "t1", "data": {"author": "user2", "body": "This is a valid long comment with enough text."}},
        {"kind": "invalid_kind"},
        {"kind": "t1", "data": {"author": "user3", "body": "This action was performed automatically."}},
    ]

    result = utils.filter_comments(comments)

    assert result == ["This is a valid long comment with enough text."]

@patch("api.services.vibe_service_utils.embedder")
def test_get_relevant_comments_filters_by_threshold(mock_embedder):
    mock_embedder.encode.side_effect = lambda _text, **_: _text
    with patch("api.services.vibe_service_utils.util.cos_sim") as mock_cos:
        mock_cos.side_effect = lambda _a, b: MagicMock(item=lambda: 0.5 if "good" in b else 0.05)
        comments = ["this is a good comment", "this is unrelated"]

        result = utils.get_relevant_comments(comments, "good topic", threshold=0.1)

        assert result == ["this is a good comment"]
        assert mock_embedder.encode.call_count == 3  # 2 comments + 1 topic

def test_run_sentiment_analysis_returns_expected_structure():
    comments = ["great post", "bad post"]
    mock_model = MagicMock()
    mock_model.side_effect = [
        [{"label": "positive", "score": 0.9}],
        [{"label": "negative", "score": 0.1}],
    ]

    result = utils.run_sentiment_analysis(comments, mock_model)

    assert len(result) == 2
    assert result[0]["label"] == "POSITIVE"
    assert result[1]["label"] == "NEGATIVE"
    assert all("score" in r for r in result)

    mock_model.assert_any_call("great post")

@patch("api.services.vibe_service_utils.get_relevant_comments", return_value=["c1", "c2"])
def test_summarise_analysed_posts_empty(mock_relevant):
    result = utils.summarise_analysed_posts([], "topic")

    assert result["vibe"] == "neutral"
    assert result["avg_sentiment"] == 0.0
    assert result["posts_analysed"] == 0
    assert result["breakdown"] == {"positive": 0, "negative": 0, "neutral": 0}

    mock_relevant.assert_not_called()

@patch("api.services.vibe_service_utils.get_relevant_comments", return_value=["c1", "c2"])
def test_summarise_analysed_posts_positive(mock_relevant):
    analysed = [
        {"text": "happy", "label": "POSITIVE", "score": 0.9},
        {"text": "good", "label": "POSITIVE", "score": 0.8},
        {"text": "bad", "label": "NEGATIVE", "score": 0.4},
    ]

    expected_avg = (2 - 1) / 3 # (positive - negative) / total
    result = utils.summarise_analysed_posts(analysed, "topic")

    assert result["vibe"] == "positive"
    assert result["avg_sentiment"] > 0
    assert result["avg_sentiment"] == pytest.approx(expected_avg, rel=0.01)
    assert result["posts_analysed"] == 3
    assert set(result["breakdown"].keys()) == {"positive", "negative", "neutral"}
    assert isinstance(datetime.fromisoformat(result["timestamp"]), datetime)

    mock_relevant.assert_called_once()

@patch("api.services.vibe_service_utils.get_relevant_comments", return_value=["rel1"])
def test_summarise_analysed_posts_negative(mock_relevant):
    analysed = [
        {"text": "bad", "label": "NEGATIVE", "score": 0.9},
        {"text": "terrible", "label": "NEGATIVE", "score": 0.8},
        {"text": "ok", "label": "NEUTRAL", "score": 0.5},
    ]

    result = utils.summarise_analysed_posts(analysed, "topic")

    assert result["vibe"] == "negative"
    assert result["avg_sentiment"] < 0

    mock_relevant.assert_called_once_with(['bad', 'terrible', 'ok'], 'topic')
