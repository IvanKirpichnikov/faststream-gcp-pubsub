from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(
    project_id="my-project",
    api_endpoint="europe-west1-pubsub.googleapis.com:443",
    client_options={"quota_project_id": "billing-project"},
)
