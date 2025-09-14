from pydantic import BaseModel

class AdaptiveKCResponse(BaseModel):
    kc_id: int | None