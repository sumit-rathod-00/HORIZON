from pydantic import BaseModel, Field


class ChangePassword(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)