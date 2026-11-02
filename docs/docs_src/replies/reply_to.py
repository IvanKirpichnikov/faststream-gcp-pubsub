from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


@broker.subscriber("jobs-worker", topic="jobs")
async def run(job: dict[str, int]) -> dict[str, int]:
    # published to the topic named by the message's `reply_to`
    return {"done": True, "job": job["id"]}


@broker.subscriber("results-client", topic="results")
async def collect(result: dict[str, int]) -> None: ...


async def submit() -> None:
    await broker.publish({"id": 7}, "jobs", reply_to="results")
