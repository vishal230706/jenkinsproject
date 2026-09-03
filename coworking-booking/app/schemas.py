from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, model_validator


class SpaceBase(BaseModel):
    name: str
    space_type: str
    capacity: int = 1


class SpaceCreate(SpaceBase):
    pass


class SpaceResponse(SpaceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookingBase(BaseModel):
    space_id: int
    user_email: EmailStr
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_time >= self.end_time:
            raise ValueError("end_time must be strictly after start_time")
        return self


class BookingCreate(BookingBase):
    pass


class BookingResponse(BookingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
