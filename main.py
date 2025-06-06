from typing import List

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


def _get_notifications(channel: str) -> List[str]:
    notifications = {"1": ["fizz"], "2": ["buzz"]}

    if channel in notifications:
        return notifications[channel]

    raise HTTPException(status_code=404, detail=f"Channel {channel} not found.")
