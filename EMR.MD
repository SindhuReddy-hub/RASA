Got it — we’ll integrate **Amazon EMR** (Elastic MapReduce) into your Rasa chatbot using **read-only AWS CLI commands**. Below are the typical **read-only EMR CLI commands** we can support:

---

### ✅ Target Read-Only EMR Commands

1. **List EMR Clusters**

   ```bash
   aws emr list-clusters
   ```
2. **Describe Specific EMR Cluster**

   ```bash
   aws emr describe-cluster --cluster-id <cluster-id>
   ```
3. **List Steps in a Cluster**

   ```bash
   aws emr list-steps --cluster-id <cluster-id>
   ```

---

## 🧠 1. `nlu.yml` – Training Examples

```yaml
version: "3.1"
nlu:
- intent: list_emr_clusters
  examples: |
    - show me the emr clusters
    - list all emr clusters
    - what emr clusters are running
    - get all emr clusters

- intent: describe_emr_cluster
  examples: |
    - describe emr cluster with id [j-1234567890](cluster_id)
    - show details of emr cluster [j-2345678901](cluster_id)
    - get info about cluster [j-abcdefg123](cluster_id)

- intent: list_emr_steps
  examples: |
    - list steps for emr cluster [j-2345678901](cluster_id)
    - what are the steps in emr cluster [j-1234567890](cluster_id)
    - show all steps in cluster [j-abcd567890](cluster_id)
```

---

## 📘 2. `domain.yml` – Additions

```yaml
version: "3.1"
intents:
  - list_emr_clusters
  - describe_emr_cluster
  - list_emr_steps

entities:
  - cluster_id

slots:
  cluster_id:
    type: text
    influence_conversation: true

responses:
  utter_ask_cluster_id:
    - text: "Please provide the EMR cluster ID."

actions:
  - action_list_emr_clusters
  - action_describe_emr_cluster
  - action_list_emr_steps
```

---

## 🎭 3. `stories.yml` – Example User Flows

```yaml
version: "3.1"
stories:
- story: list EMR clusters
  steps:
    - intent: list_emr_clusters
    - action: action_list_emr_clusters

- story: describe EMR cluster
  steps:
    - intent: describe_emr_cluster
      entities:
        - cluster_id: "j-1234567890"
    - action: action_describe_emr_cluster

- story: list EMR steps
  steps:
    - intent: list_emr_steps
      entities:
        - cluster_id: "j-1234567890"
    - action: action_list_emr_steps
```

---

## ⚙️ 4. `actions.py` – Custom Actions

```python
import subprocess
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionListEmrClusters(Action):
    def name(self):
        return "action_list_emr_clusters"

    def run(self, dispatcher, tracker, domain):
        try:
            result = subprocess.run(
                ["aws", "emr", "list-clusters"],
                capture_output=True, text=True, check=True
            )
            dispatcher.utter_message(text=f"Here are the EMR clusters:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"Failed to fetch EMR clusters:\n{e.stderr}")
        return []

class ActionDescribeEmrCluster(Action):
    def name(self):
        return "action_describe_emr_cluster"

    def run(self, dispatcher, tracker, domain):
        cluster_id = tracker.get_slot("cluster_id")
        if not cluster_id:
            dispatcher.utter_message(response="utter_ask_cluster_id")
            return []
        try:
            result = subprocess.run(
                ["aws", "emr", "describe-cluster", "--cluster-id", cluster_id],
                capture_output=True, text=True, check=True
            )
            dispatcher.utter_message(text=f"Cluster details:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"Failed to describe cluster:\n{e.stderr}")
        return []

class ActionListEmrSteps(Action):
    def name(self):
        return "action_list_emr_steps"

    def run(self, dispatcher, tracker, domain):
        cluster_id = tracker.get_slot("cluster_id")
        if not cluster_id:
            dispatcher.utter_message(response="utter_ask_cluster_id")
            return []
        try:
            result = subprocess.run(
                ["aws", "emr", "list-steps", "--cluster-id", cluster_id],
                capture_output=True, text=True, check=True
            )
            dispatcher.utter_message(text=f"Steps in cluster {cluster_id}:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            dispatcher.utter_message(text=f"Failed to list steps:\n{e.stderr}")
        return []
```

---
Perfect! Let’s refactor your chatbot to **use a form** for collecting the `cluster_id` when the user asks to describe a cluster or list its steps.

---

## 🔁 Updated Flow with Slot Filling via Forms

We’ll use a **single form** to request the `cluster_id` for both:

* `describe_emr_cluster`
* `list_emr_steps`

---

## 🧠 1. `nlu.yml` (Add example for providing cluster\_id)

Add this if not already present:

```yaml
- intent: provide_cluster_id
  examples: |
    - The cluster ID is [j-1234567890](cluster_id)
    - It's [j-2345678901](cluster_id)
    - [j-abcdefg123](cluster_id)
```

---

## 📘 2. `domain.yml` (Add form and slot config)

```yaml
version: "3.1"

intents:
  - list_emr_clusters
  - describe_emr_cluster
  - list_emr_steps
  - provide_cluster_id

entities:
  - cluster_id

slots:
  cluster_id:
    type: text
    influence_conversation: true
    mappings:
      - type: from_entity
        entity: cluster_id
        conditions:
          - active_loop: cluster_id_form

responses:
  utter_ask_cluster_id:
    - text: "Please provide the EMR cluster ID."

forms:
  cluster_id_form:
    required_slots:
      - cluster_id

actions:
  - action_list_emr_clusters
  - action_describe_emr_cluster
  - action_list_emr_steps
  - cluster_id_form
```

---

## 🎭 3. `stories.yml` – Updated with form activation

```yaml
version: "3.1"
stories:
- story: list EMR clusters
  steps:
    - intent: list_emr_clusters
    - action: action_list_emr_clusters

- story: describe EMR cluster with form
  steps:
    - intent: describe_emr_cluster
    - action: cluster_id_form
    - active_loop: cluster_id_form
    - slot_was_set:
        - cluster_id: "j-1234567890"
    - active_loop: null
    - action: action_describe_emr_cluster

- story: list EMR steps with form
  steps:
    - intent: list_emr_steps
    - action: cluster_id_form
    - active_loop: cluster_id_form
    - slot_was_set:
        - cluster_id: "j-1234567890"
    - active_loop: null
    - action: action_list_emr_steps
```

---

## ⚙️ 4. `actions.py` – No change to action code

Your `actions.py` functions like `action_describe_emr_cluster` and `action_list_emr_steps` already use `tracker.get_slot("cluster_id")`, so they’ll automatically work with the form.

---

### ✅ Resulting Behavior

* When a user asks to describe or list steps for a cluster but **doesn't provide a cluster ID**, the **`cluster_id_form`** will ask for it.
* Once the form is filled, the action will run.

---



