from typing import AsyncGenerator, Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from redis.asyncio import Redis

from utils import get_env

load_dotenv()

app = FastAPI()

redis = Redis(
    host=get_env("REDIS_HOST"), port=get_env("REDIS_PORT", int), password=get_env("REDIS_PASSWORD"), ssl=True
)


@app.get("/{channel}", response_class=StreamingResponse)
async def get_notifications(channel: str | None) -> StreamingResponse:
    return StreamingResponse(
        _get_notifications(channel),
        media_type="text/event-stream"
    )


async def _get_notifications(channel: str) -> AsyncGenerator[str, None]:
    async with redis.pubsub() as pubsub:
        await pubsub.subscribe(f"notifications/{channel}")

        async for message in pubsub.listen():
            if message["type"] == "message":
                data: str = message["data"].decode("utf-8")

                yield f"event: message\ndata: {data}\n\n"


@app.post("/{channel}", status_code=204)
async def post_notification(channel: str, message: Annotated[str, Body(embed=True)]) -> None:
    await redis.publish(f"notifications/{channel}", message)
