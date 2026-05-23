from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime

class RoomBookingSchema(BaseModel):
    guest_name: str = Field(..., description="First and last name of the guest.")
    room_type: str = Field(..., description="Must be one of: Single, Double, Suite, Penthouse.")
    check_in_date: str = Field(..., description="ISO format YYYY-MM-DD.")
    check_out_date: str = Field(..., description="ISO format YYYY-MM-DD.")

    # full name check
    @field_validator('guest_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip().split()) < 2:
            raise ValueError("Guest name must contain both a first and last name.")
        return v.strip()

    # room check
    @field_validator('room_type')
    @classmethod
    def validate_room_type(cls, v: str) -> str:
        valid_types = ["Single", "Double", "Suite", "Penthouse"]
        formatted_type = v.strip().capitalize()
        if formatted_type not in valid_types:
            raise ValueError(f"Room type must be exactly one of {valid_types}.")
        return formatted_type

    #  dates check
    @field_validator('check_in_date', 'check_out_date')
    @classmethod
    def validate_future_dates(cls, v: str) -> str:
        today = datetime.today().date()
        try:
            date_val = datetime.strptime(v.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be in proper YYYY-MM-DD format.")
        
        if date_val < today:
            raise ValueError("Dates cannot be in the past.")
        return v.strip()

    #  dates check 2
    @model_validator(mode="after")
    def validate_date_order(self) -> "RoomBookingSchema":
        try:
            in_date = datetime.strptime(self.check_in_date, "%Y-%m-%d").date()
            out_date = datetime.strptime(self.check_out_date, "%Y-%m-%d").date()
            
            if out_date <= in_date:
                raise ValueError("Check-out date must be strictly after the check-in date.")
        except ValueError as e:
            
            raise ValueError(str(e))
            
        return self