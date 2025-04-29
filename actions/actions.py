# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import subprocess
import json
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# --- Lambda Operations ---
class ActionLambdaOperations(Action):
    def name(self) -> Text:
        return "action_lambda_operations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_intent = tracker.latest_message['intent'].get('name')
        lambda_function_name = next(tracker.get_latest_entity_values("function_name"), None)

        try:
            if latest_intent == "list_lambda_functions":
                dispatcher.utter_message(text="Fetching list of Lambda functions...")
                result = subprocess.run(
                    ["aws", "lambda", "list-functions", "--region", "us-east-1"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = json.loads(result.stdout)
                functions = output.get('Functions', [])
                if functions:
                    function_names = [f"• {fn['FunctionName']}" for fn in functions]
                    dispatcher.utter_message(text="\n".join(function_names))
                else:
                    dispatcher.utter_message(text="No Lambda functions found.")

            elif latest_intent == "invoke_lambda_function" and lambda_function_name:
                dispatcher.utter_message(text=f"Invoking Lambda function: {lambda_function_name}")
                response_file = "/tmp/lambda_response.json"
                result = subprocess.run(
                    ["aws", "lambda", "invoke",
                     "--function-name", lambda_function_name,
                     response_file,
                     "--region", "us-east-1"],
                    capture_output=True,
                    text=True,
                    check=True
                )
             if os.path.exists(response_file):
    with open(response_file, "r") as f:
        response_content = f.read()
                dispatcher.utter_message(text=f"Lambda Response:\n{response_content}")

            else:
                dispatcher.utter_message(text="Sorry, I didn't understand which Lambda operation to perform.")

        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"Command failed: {e.stderr}")
        except Exception as e:
            dispatcher.utter_message(text=f"An unexpected error occurred: {str(e)}")

        return []

# --- S3 Operations ---
class ActionS3Operations(Action):
    def name(self) -> Text:
        return "action_s3_operations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_intent = tracker.latest_message['intent'].get('name')
        bucket_name = next(tracker.get_latest_entity_values("bucket_name"), None)
        object_key = next(tracker.get_latest_entity_values("object_key"), None)
        local_file_path = next(tracker.get_latest_entity_values("local_file_path"), None)

        try:
            if latest_intent == "list_s3_buckets":
                dispatcher.utter_message(text="Fetching list of S3 buckets...")
                result = subprocess.run(
                    ["aws", "s3api", "list-buckets", "--region", "us-east-1"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = json.loads(result.stdout)
                buckets = output.get('Buckets', [])
                if buckets:
                    bucket_names = [f"• {b['Name']}" for b in buckets]
                    dispatcher.utter_message(text="\n".join(bucket_names))
                else:
                    dispatcher.utter_message(text="No S3 buckets found.")

            elif latest_intent == "list_s3_objects" and bucket_name:
                dispatcher.utter_message(text=f"Fetching objects in S3 bucket: {bucket_name}")
                result = subprocess.run(
                    ["aws", "s3api", "list-objects-v2",
                     "--bucket", bucket_name,
                     "--region", "us-east-1"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                output = json.loads(result.stdout)
                objects = output.get('Contents', [])
                if objects:
                    object_keys = [f"• {obj['Key']}" for obj in objects]
                    dispatcher.utter_message(text="\n".join(object_keys))
                else:
                    dispatcher.utter_message(text=f"No objects found in {bucket_name}.")

            elif latest_intent == "download_s3_object" and bucket_name and object_key:
                dispatcher.utter_message(text=f"Downloading {object_key} from {bucket_name}...")
                local_path = f"/tmp/{object_key.split('/')[-1]}"  # Save it in /tmp
                subprocess.run(
                    ["aws", "s3", "cp",
                     f"s3://{bucket_name}/{object_key}",
                     local_path],
                    check=True
                )
                dispatcher.utter_message(text=f"Downloaded {object_key} to {local_path}")

            elif latest_intent == "upload_s3_object" and bucket_name and local_file_path:
                dispatcher.utter_message(text=f"Uploading {local_file_path} to {bucket_name}...")
                subprocess.run(
                    ["aws", "s3", "cp",
                     local_file_path,
                     f"s3://{bucket_name}/"],
                    check=True
                )
                dispatcher.utter_message(text=f"Uploaded {local_file_path} to {bucket_name}")

            else:
                dispatcher.utter_message(text="Sorry, I didn't understand which S3 operation to perform.")

        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"Command failed: {e.stderr}")
        except Exception as e:
            dispatcher.utter_message(text=f"An unexpected error occurred: {str(e)}")

        return []


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import subprocess
import json

class ActionManageStepFunctions(Action):
    def name(self) -> Text:
        return "action_manage_stepfunctions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Find the latest user intent
        latest_intent = tracker.get_intent_of_latest_message()
        dispatcher.utter_message(text=f"Detected intent: {latest_intent}")

        if latest_intent == "list_step_functions":
            return self.list_step_functions(dispatcher)
        
        elif latest_intent == "start_step_function_execution":
            return self.start_step_function_execution(dispatcher, tracker)
        
        else:
            dispatcher.utter_message(text="I'm not sure how to handle this step function request.")
            return []

    def list_step_functions(self, dispatcher):
        try:
            dispatcher.utter_message(text="Fetching list of Step Functions...")

            output_text = subprocess.check_output(
                ["aws", "stepfunctions", "list-state-machines", "--region", "us-east-1"],
                text=True
            )
            output_json = json.loads(output_text)

            state_machines = output_json.get('stateMachines', [])
            if state_machines:
                names = [f"• {sm['name']}" for sm in state_machines]
                dispatcher.utter_message(text="\n".join(names))
            else:
                dispatcher.utter_message(text="No state machines found.")

        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"Command failed: {e.output}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []

    def start_step_function_execution(self, dispatcher, tracker):
        try:
            state_machine_name = next(tracker.get_latest_entity_values("state_machine_name"), None)
            if not state_machine_name:
                dispatcher.utter_message(text="Please specify the state machine name to start.")
                return []

            dispatcher.utter_message(text=f"Starting execution of state machine: {state_machine_name}...")

            # Find the full ARN
            list_output = subprocess.check_output(
                ["aws", "stepfunctions", "list-state-machines", "--region", "us-east-1"],
                text=True
            )
            list_json = json.loads(list_output)
            state_machines = list_json.get('stateMachines', [])

            matching_machine = next((sm for sm in state_machines if sm['name'] == state_machine_name), None)

            if not matching_machine:
                dispatcher.utter_message(text=f"No state machine found with name: {state_machine_name}")
                return []

            state_machine_arn = matching_machine['stateMachineArn']

            # Start execution
            start_output = subprocess.check_output(
                ["aws", "stepfunctions", "start-execution", "--state-machine-arn", state_machine_arn],
                text=True
            )

            dispatcher.utter_message(text=f"Execution started successfully for {state_machine_name}!")

        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"Command failed: {e.output}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []

