from typing import List

from pydantic import ValidationError, validator, BaseModel
from pydantic.fields import ModelField
from sqlalchemy import Column, Integer, Float, ARRAY, String, ForeignKey

from app.utils import Base


class Order(BaseModel):
    order_id: int
    weight: float
    region: int
    delivery_hours: List[str]

    @validator("weight")
    def validate_weight(cls, weight, field: ModelField):
        if 0.01 > weight or weight > 50:
            raise ValidationError()
        return weight


class CompleteOrder(BaseModel):
    courier_id: int
    order_id: int
    complete_time: str


class OrderList(BaseModel):
    data: List[Order]


class OrderModel(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    weight = Column(Float)
    region = Column(Integer)
    delivery_hours = Column(ARRAY(String))
    courier_id = Column(Integer, ForeignKey("couriers.courier_id", ondelete="CASCADE"))

    def as_dict(self):
        d = {
            "order_id": self.order_id,
            "weight": self.weight,
            "region": self.region,
            "delivery_hours": self.delivery_hours,
        }

        return d
