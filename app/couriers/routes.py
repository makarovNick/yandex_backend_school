from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.couriers.models import CourierList, CourierModel, PatchCourier
from app.utils import get_db
from app.utils import get_rating, get_coeff
from fastapi import APIRouter

router = APIRouter(prefix="/couriers")


@router.post("")
async def download_couriers(couriers: CourierList, db: Session = Depends(get_db)):
    for courier in couriers.data:
        new_c = CourierModel(
            courier_id=courier.courier_id,
            courier_type=courier.courier_type,
            regions=courier.regions,
            working_hours=courier.working_hours,
            counts=[0 for i in courier.regions],
            mean_times=[0 for i in courier.regions],
        )

        db.add(new_c)
        db.commit()
        db.refresh(new_c)

    return JSONResponse({"couriers": [{"id": id.courier_id} for id in couriers.data]})


@router.patch("/{courier_id}")
async def patch_courier(courier_id: int, data: PatchCourier, db: Session = Depends(get_db)):
    cur_c = db.query(CourierModel).get(courier_id)
    if data.courier_type:
        cur_c.courier_type = data.courier_type
    if data.regions:
        cur_c.regions = data.regions
        cur_c.mean_times = [0 for i in data.regions]
        cur_c.counts = [0 for i in data.regions]
    if data.working_hours:
        cur_c.working_hours = data.working_hours

    db.commit()
    # db.refresh(cur_c)

    return JSONResponse(cur_c.as_dict())


@router.get("/{courier_id}")
async def get_courier(courier_id: int, db: Session = Depends(get_db)):
    cur_c = db.query(CourierModel).get(courier_id)
    if not cur_c:
        raise HTTPException(status_code=404)

    d = cur_c.as_dict()
    s = sum(cur_c.counts)
    if s:
        d["rating"] = get_rating(
            min(
                cur_c.mean_times[i] / cur_c.counts[i]
                for i in range(len(cur_c.mean_times))
                if cur_c.counts[i] != 0
            )
        )

    d["earnings"] = 500 * s * get_coeff(cur_c.courier_type)

    return JSONResponse(d)
