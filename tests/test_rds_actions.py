import pytest
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker
from unittest.mock import patch
from actions import (
    ActionListRDSInstances,
    ActionDescribeRDSInstance,
    ActionStartRDSInstance,
    ActionStopRDSInstance,
)

def create_tracker(slots):
    return Tracker(sender_id="test_user", slots=slots, latest_message={}, events=[], paused=False, followup_action=None, active_loop={}, latest_action_name=None)

def test_list_rds_instances():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker({})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b'test-db prod-db'
        action = ActionListRDSInstances()
        events = action.run(dispatcher, tracker, domain)
        assert "test-db" in dispatcher.messages[0]["text"]

def test_describe_rds_instance():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker({"db_instance_identifier": "test-db"})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b'Status: available\nEngine: mysql\n'
        action = ActionDescribeRDSInstance()
        events = action.run(dispatcher, tracker, domain)
        assert "Status: available" in dispatcher.messages[0]["text"]

def test_start_rds_instance():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker({"db_instance_identifier": "prod-db"})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b'Starting instance'
        action = ActionStartRDSInstance()
        events = action.run(dispatcher, tracker, domain)
        assert "starting" in dispatcher.messages[0]["text"].lower()

def test_stop_rds_instance():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker({"db_instance_identifier": "test-db"})
    domain = {}

    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b'Stopping instance'
        action = ActionStopRDSInstance()
        events = action.run(dispatcher, tracker, domain)
        assert "stopping" in dispatcher.messages[0]["text"].lower()
