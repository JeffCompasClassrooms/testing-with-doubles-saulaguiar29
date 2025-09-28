import os
import pickle
import pytest
from unittest.mock import patch, mock_open
from mydb import MyDB

# fixtures that create and clean up the patches

@pytest.fixture
def mock_isfile():
    p = patch("os.path.isfile", return_value=False)
    m = p.start()
    try:
        yield m
    finally:
        p.stop()

@pytest.fixture
def mock_open_func():
    p = patch("builtins.open", mock_open())
    m = p.start()

    try:
        yield m
    finally:
        p.stop()


@pytest.fixture  
def mock_dump():
    p = patch("pickle.dump")
    m = p.start()

    try:
        yield m
    finally:
        p.stop()

# Test uses the fixtures via parameters
def test_creates_empty_database_if_file_does_not_exist(mock_isfile, mock_open_func, mock_dump):
    db = MyDB("mydatabase.db")

    mock_isfile.assert_called_once_with("mydatabase.db")
    mock_open_func.assert_called_once_with("mydatabase.db", "wb")
    mock_dump.assert_called_once_with([], mock_open_func.return_value)
