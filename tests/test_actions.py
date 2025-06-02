import pytest
from actions import (
    ActionListS3Buckets,
    ActionListFilesInBucket,
    ActionDownloadFile,
    ActionUploadFile,
)
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk import Tracker
from unittest.mock import patch

def create_tracker_with_slots(slots):
    return Tracker(sender_id="test", slots=slots, latest_message={}, events=[], paused=False, followup_action=None, active_loop={}, latest_action_name=None)

def test_list_s3_buckets():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker_with_slots({})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b'{"Buckets":[{"Name":"my-bucket"},{"Name":"logs"}]}'
        action = ActionListS3Buckets()
        events = action.run(dispatcher, tracker, domain)
        assert "my-bucket" in dispatcher.messages[0]["text"]

def test_list_files_in_bucket():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker_with_slots({"bucket_name": "my-bucket"})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b'report.csv\nsummary.txt\n'
        action = ActionListFilesInBucket()
        events = action.run(dispatcher, tracker, domain)
        assert "report.csv" in dispatcher.messages[0]["text"]

def test_download_file():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker_with_slots({"bucket_name": "my-bucket", "file_name": "report.csv"})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b''
        action = ActionDownloadFile()
        events = action.run(dispatcher, tracker, domain)
        assert "downloaded" in dispatcher.messages[0]["text"].lower()

def test_upload_file():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker_with_slots({"bucket_name": "my-bucket"})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b''
        action = ActionUploadFile()
        events = action.run(dispatcher, tracker, domain)
        assert "uploaded" in dispatcher.messages[0]["text"].lower()
