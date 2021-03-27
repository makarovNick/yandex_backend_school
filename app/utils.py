from datetime import timedelta, datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_rating(t):
    return (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5


def get_time_timestamp(time: str):
    hour = int(time[:2])
    minutes = int(time[3:])
    now = datetime.now()
    return (
        now.replace(hour=0, minute=0, second=0, microsecond=0)
        + timedelta(hours=hour, minutes=minutes)
    ).timestamp()


class IsInComp:
    def __init__(self, courier_times):
        self.courier_times = courier_times

    def is_in(self, orders):
        res = []
        for courier_time in self.courier_times:
            start1, end1 = courier_time.split("-", 1)
            for order_time in orders.delivery_hours:
                start2, end2 = order_time.split("-", 1)
                if start1 <= start2 <= end1 or start1 >= start2 and end1 <= end2:
                    return True

        return False


def timestamp_from_iso(time: str):
    return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()


def get_coeff(type: str):
    if type == "foot":
        return 2
    elif type == "bike":
        return 5

    return 9


def time_now():
    return datetime.now()
