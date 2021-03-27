from typing import List, Optional

from pydantic.main import BaseModel
from sqlalchemy import Column, Integer, String, ARRAY, Float
from sqlalchemy.orm import relationship

from app.utils import Base


class CourierId(BaseModel):
    courier_id: int


class Courier(BaseModel):
    courier_id: int
    courier_type: str  # TODO
    regions: List[Optional[int]]
    working_hours: List[Optional[str]]  # TODO

    class Config:
        orm_mode = True


class PatchCourier(BaseModel):
    courier_type: Optional[str]
    regions: Optional[List[Optional[int]]]
    working_hours: Optional[List[Optional[str]]]

    class Config:
        orm_mode = True


class CourierList(BaseModel):
    data: List[Courier]



class CourierModel(Base):
    __tablename__ = "couriers"

    courier_id = Column(Integer, primary_key=True)
    courier_type = Column(String)
    regions = Column(ARRAY(Integer))
    working_hours = Column(ARRAY(String))
    mean_times = Column(ARRAY(Integer))
    previous = Column(Float, default=0)  # Unix timestamp
    # earnings = Column(Integer)
    counts = Column(ARRAY(Integer))
    orders = relationship("OrderModel")

    def as_dict(self):
        d = {
            "courier_id": self.courier_id,
            "courier_type": self.courier_type,
            "regions": self.regions,
            "working_hours": self.working_hours,
        }
        return d