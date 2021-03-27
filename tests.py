import pytest

from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import and_
from app.couriers.models import CourierModel
from app.main import app
import random

from app.orders.models import OrderModel
from app.utils import IsInComp, timestamp_from_iso, time_now, get_rating, get_coeff, SessionLocal, engine
from app.main import Base

client = TestClient(app)


def minutes_to_time(n):
    hours = str(n // 60)
    minutes = str(n % 60)
    if len(hours) == 1:
        hours = "0" + hours
    if len(minutes) == 1:
        minutes = "0" + minutes

    return hours + ":" + minutes


def get_random_times():
    res = []
    start = random.randint(0, 1200)
    while start < 1350:
        end = random.randint(start + 90, 1440)
        res.append(minutes_to_time(start) + "-" + minutes_to_time(end))
        start = end + 90

    return res


def get_regions():
    res = list(range(20))
    n = random.randint(1, 10)
    random.shuffle(res)

    return res[:n]


def get_type():
    return random.choice(["foot", "bike", "car"])


def get_random_courier(id):
    return {
        "courier_id": id,
        "courier_type": get_type(),
        "regions": get_regions(),
        "working_hours": get_random_times(),
    }


def get_random_orders(id):
    return {
        "order_id": id,
        "weight": random.random() * 49.98 + 0.01,
        "region": random.choice(get_regions()),
        "delivery_hours": get_random_times(),
    }


def test_couriers():
    data = {
        "data": [
            get_random_courier(i) for i in range(100)
        ]
    }

    response = client.post("/couriers", json=data)

    assert response.status_code == 200
    assert response.json() == {"couriers": [{"id": i} for i in range(100)]}


def test_failed_couriers():
    data = {
        "data": [
            get_random_courier(i) for i in range(100, 110)
        ]
    }
    fields = ["courier_type", "regions", "working_hours"]
    for i in range(10):
        if i % 2 == 0:
            data["data"][i].pop(fields[i % 3], None)

    response = client.post("/couriers", json=data)

    assert response.status_code == 400
    assert response.json() == {"validation_error": {
        "couriers": [{"id": i} for i in range(100, 110, 2)]}
    }


def test_orders():
    data = {
        "data": [
            get_random_orders(i) for i in range(1000)
        ]
    }
    response = client.post("/orders", json=data)

    assert response.status_code == 200
    assert response.json() == {"orders": [{"id": i} for i in range(1000)]}


def test_failed_orders():
    data = {
        "data": [
            get_random_orders(i) for i in range(1000, 1010)
        ]
    }

    fields = ["weight", "region", "delivery_hours"]
    for i in range(10):
        if i % 2 == 0:
            if i % 3 == 0:
                data["data"][i]['weight'] = random.choice([0.001, 51])
            else:
                data["data"][i].pop(fields[i % 3], None)

    response = client.post("/orders", json=data)

    assert response.status_code == 400
    assert response.json() == {"validation_error": {
        "orders": [{"id": i} for i in range(1000, 1010, 2)]
    }
    }


def test_assign_order():
    data = {
        "courier_id": random.randint(0, 101)
    }
    db = SessionLocal()
    cur_c = db.query(CourierModel).get(data["courier_id"])
    max_weight = 50
    if cur_c.courier_type == "foot":
        max_weight = 10
    elif cur_c.courier_type == "bike":
        max_weight = 15

    comp = IsInComp(cur_c.working_hours)
    cur_o = db.query(OrderModel).filter(and_(OrderModel.weight <= max_weight),
                                        (OrderModel.region.in_(cur_c.regions))).all()
    cur_o = list(filter(comp.is_in, cur_o))

    response = client.post("/orders/assign", json=data)

    res_json = response.json()

    assert response.status_code == 200
    assert sorted([o["id"] for o in res_json["orders"]]) == sorted(o.order_id for o in cur_o)
    assert abs(timestamp_from_iso(res_json["assign_time"]) - time_now().timestamp()) < 10


def test_order_complete():
    db = SessionLocal()
    cur_o = db.query(OrderModel).filter(OrderModel.courier_id.isnot(None)).all()

    for order in cur_o:
        cur_c = db.query(CourierModel).get(order.courier_id)
        data = {
            "courier_id": order.courier_id,
            "order_id": order.order_id,
            "complete_time": datetime.fromtimestamp(cur_c.previous + 1800).isoformat()[:-3] + "Z",
        }

        response = client.post("/orders/complete", json=data)
        db.refresh(cur_c)
        assert response.status_code == 200
        assert response.json()["order_id"] == order.order_id


def test_courier_info():
    db = SessionLocal()

    cur_c = db.query(CourierModel).filter(CourierModel.previous != 0).first()

    response = client.get(f"/couriers/{cur_c.courier_id}")
    res_json = response.json()
    assert response.status_code == 200

    s = sum(cur_c.counts)
    d = cur_c.as_dict()
    if s:
        d["rating"] = get_rating(
            min(
                cur_c.mean_times[i] / cur_c.counts[i]
                for i in range(len(cur_c.mean_times))
                if cur_c.counts[i] != 0
            )
        )

    d["earnings"] = 500 * s * get_coeff(cur_c.courier_type)

    assert res_json == d


@pytest.fixture()
def cleanup(request):
    def drop():
        Base.metadata.drop_all(bind=engine)

    request.addfinalizer(drop)
