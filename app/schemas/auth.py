from pydantic import BaseModel

class TokenVerifyOut(BaseModel):
    uid: str
    email: str | None = None
    name: str | None = None