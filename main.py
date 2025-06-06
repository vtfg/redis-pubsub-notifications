import asyncio
from typing import AsyncGenerator, Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from redis.asyncio import Redis

from utils import get_env

load_dotenv()

config = {
    "REDIS_HOST": get_env("REDIS_HOST"),
    "REDIS_PORT": get_env("REDIS_PORT"),
    "REDIS_PASSWORD": get_env("REDIS_PASSWORD"),
}
app = FastAPI()

client = Redis(
    host=config.get("REDIS_HOST"), port=config.get("REDIS_PORT"), password=config.get("REDIS_PASSWORD"), ssl=True
)


@app.get("/{channel}", response_class=StreamingResponse)
async def get_notifications(channel: str | None) -> StreamingResponse:
    return StreamingResponse(
        _get_notifications(channel),
        media_type="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Content-Encoding": "none",
        },
    )


async def _get_notifications(channel: str) -> AsyncGenerator[str, None]:
    async with client.pubsub() as pubsub:
        await pubsub.subscribe(f"notifications/{channel}")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)

            if message:
                data: bytes = message["data"].decode("utf-8")

                yield f"event: message\ndata: {str(data)}\n\n"

                await asyncio.sleep(1)


@app.post("/{channel}", status_code=204)
async def post_notification(channel: str, message: Annotated[str, Body(embed=True)]) -> None:
    await client.publish(f"notifications/{channel}", message)
