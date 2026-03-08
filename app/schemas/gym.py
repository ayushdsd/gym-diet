from pydantic import BaseModel


class GymCreate(BaseModel):
    name: str
    location: str


class GymOut(BaseModel):
    id: int
    name: str
    location: str

    class Config:
        from_attributes = True

