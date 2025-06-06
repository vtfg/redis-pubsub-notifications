import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

notifications = {"1": ["fizz", "buzz"], "2": ["foo", "bar"]}


@app.get("/{channel}", response_class=StreamingResponse)
async def get_notifications(channel: str | None) -> StreamingResponse:
    if channel not in notifications:
        raise HTTPException(status_code=404, detail=f"Channel {channel} not found.")

    return StreamingResponse(
        _get_notifications(channel),
        media_type="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Content-Encoding": "none",
        },
    )


async def _get_notifications(channel: str) -> AsyncGenerator[str, None]:
    for notification in notifications[channel]:
        yield f"data: {notification}\n\n"

        await asyncio.sleep(1)
