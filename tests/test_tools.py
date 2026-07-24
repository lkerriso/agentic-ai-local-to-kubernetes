import inspect
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.websearch_agent.tools import web_search


def _mock_ddgs(results):
    """Build a mock DDGS context manager returning the given text results."""
    instance = MagicMock()
    instance.text.return_value = results
    ddgs = MagicMock()
    ddgs.return_value.__enter__.return_value = instance
    ddgs.return_value.__exit__.return_value = False
    return ddgs, instance


def test_web_search_exists():
    """Test that the web_search function is properly defined."""
    assert web_search is not None
    assert callable(web_search)


def test_web_search_basic_invocation():
    """Test that web_search can be called with a string query."""
    ddgs, instance = _mock_ddgs(
        [{"title": "Red Hat", "href": "https://redhat.com", "body": "Open source"}]
    )
    with patch("src.websearch_agent.tools.DDGS", ddgs):
        result = web_search("RedHat")

    assert isinstance(result, list)
    assert len(result) == 1
    assert "Red Hat" in result[0]
    assert "https://redhat.com" in result[0]
    instance.text.assert_called_once_with("RedHat", max_results=5)


def test_web_search_return_type():
    """Test that web_search returns a list of strings."""
    ddgs, _ = _mock_ddgs(
        [
            {"title": "A", "href": "https://a.com", "body": "aaa"},
            {"title": "B", "href": "https://b.com", "body": "bbb"},
        ]
    )
    with patch("src.websearch_agent.tools.DDGS", ddgs):
        result = web_search("test query")

    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)


def test_web_search_max_results_passthrough():
    """Test that max_results is forwarded to the search client."""
    ddgs, instance = _mock_ddgs([])
    with patch("src.websearch_agent.tools.DDGS", ddgs):
        result = web_search("query", max_results=3)

    assert result == []
    instance.text.assert_called_once_with("query", max_results=3)


def test_web_search_handles_missing_fields():
    """Test that results missing title/href/body do not raise."""
    ddgs, _ = _mock_ddgs([{}])
    with patch("src.websearch_agent.tools.DDGS", ddgs):
        result = web_search("query")

    assert result == [" |  | "]


def test_web_search_docstring():
    """Test that web_search has proper documentation."""
    assert web_search.__doc__ is not None
    assert "Search the web" in web_search.__doc__
    assert "Args:" in web_search.__doc__
    assert "Returns:" in web_search.__doc__


def test_web_search_function_signature():
    """Test that web_search has the correct function signature."""
    sig = inspect.signature(web_search)
    params = list(sig.parameters)
    assert params == ["query", "max_results"]
    assert sig.parameters["max_results"].default == 5


def test_web_search_type_hints():
    """Test that web_search has proper type hints."""
    hints = inspect.get_annotations(web_search)
    assert hints["query"] is str
    assert hints["max_results"] is int
    assert hints["return"] == list[str]
