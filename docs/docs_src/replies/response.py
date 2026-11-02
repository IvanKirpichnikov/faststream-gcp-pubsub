from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker, PubSubResponse

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


@broker.subscriber("jobs-worker", topic="jobs")
async def run(job: dict[str, str]) -> PubSubResponse:
    return PubSubResponse(
        {"done": True},
        headers={"worker": "w1"},
        ordering_key=job["owner"],
    )


@broker.subscriber("results-client", topic="results")
async def collect(result: dict[str, int]) -> None: ...
