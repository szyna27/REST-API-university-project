from pydantic import BaseModel


class ForbiddenName(BaseModel):
    id: int
    name: str
    reason: str | None = None

    class Config:
        from_attributes = True
