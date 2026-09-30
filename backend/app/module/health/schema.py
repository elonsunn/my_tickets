from typing import Literal

from pydantic import BaseModel


class ReadinessProbeResponse(BaseModel):
    status: Literal["ok", "unavailable"]
