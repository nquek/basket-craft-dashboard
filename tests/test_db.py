from unittest.mock import MagicMock, patch

import db


def _make_mock_conn(row):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = row
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


def test_get_headline_metrics_returns_correct_dict():
    db.get_headline_metrics.clear()
    mock_conn = _make_mock_conn((50000.0, 1500, 3000, 45000.0, 1400, 2800))
    with patch("db._connect", return_value=mock_conn):
        result = db.get_headline_metrics()
    assert result == {
        "revenue_current": 50000.0,
        "orders_current": 1500,
        "items_current": 3000,
        "revenue_prior": 45000.0,
        "orders_prior": 1400,
        "items_prior": 2800,
    }
