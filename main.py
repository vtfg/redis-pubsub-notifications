import asyncio
from typing import List, AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()


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
    notifications = {"1": ["fizz", "buzz"], "2": ["foo", "bar"]}

    if channel not in notifications:
        raise HTTPException(status_code=404, detail=f"Channel {channel} not found.")

    for notification in notifications[channel]:
        await asyncio.sleep(1)

        yield f"Notification received: {notification}\n"
