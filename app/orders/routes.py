from fastapi import Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.couriers.models import CourierModel, CourierId
from app.utils import get_db
from app.orders.models import CompleteOrder, OrderModel, OrderList
from app.utils import timestamp_from_iso, time_now, IsInComp
from fastapi import APIRouter

router = APIRouter(prefix="/orders")


@router.post("")
async def download_orders(orders: OrderList, db: Session = Depends(get_db)):
    for order in orders.data:
        new_o = OrderModel(
            order_id=order.order_id,
            weight=order.weight,
            region=order.region,
            delivery_hours=order.delivery_hours,
        )

        db.add(new_o)
        db.commit()
        db.refresh(new_o)

    return JSONResponse({"orders": [{"id": id.order_id} for id in orders.data]})


@router.post("/assign")
async def assign_orders(courier: CourierId, db: Session = Depends(get_db)):
    cur_c = db.query(CourierModel).get(courier.courier_id)
    max_weight = 50
    if cur_c.courier_type == "foot":
        max_weight = 10
    elif cur_c.courier_type == "bike":
        max_weight = 15

    # cur_time = min(cur_c.previous,
    comp = IsInComp(cur_c.working_hours)
    cur_o = (
        db.query(OrderModel)
        .filter(
            and_(OrderModel.weight <= max_weight),
            (OrderModel.region.in_(cur_c.regions)),
        )
        .all()
    )
    cur_o = list(filter(comp.is_in, cur_o))

    ids = [o.order_id for o in cur_o]
    cur_c.orders.extend(cur_o)

    if not ids:
        return JSONResponse({"orders": []})

    if cur_c.previous < 1:
        cur_c.previous = time_now().timestamp()

    db.commit()

    return JSONResponse({
        "orders": [{"id": id} for id in ids],
        "assign_time": time_now().isoformat()[:-3] + "Z",
    })


@router.post("/complete")
async def complete_order(order: CompleteOrder, db: Session = Depends(get_db)):
    cur_c = db.query(CourierModel).get(order.courier_id)
    cur_o = db.query(OrderModel).get(order.order_id)
    if cur_o.courier_id != order.courier_id or not cur_c or not cur_o:
        raise HTTPException(status_code=404)

    time = timestamp_from_iso(order.complete_time)
    ind = cur_c.regions.index(cur_o.region)

    new_time = [i for i in cur_c.mean_times]
    new_time[ind] += time - cur_c.previous
    new_arr = [j for j in cur_c.counts]
    new_arr[ind] += 1
    cur_c.counts = new_arr
    cur_c.mean_times = new_time
    cur_c.previous = time

    db.commit()

    db.delete(cur_o)
    db.commit()

    return JSONResponse({"order_id": order.order_id})
