from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models import Booking, Space
from app.schemas import BookingCreate, BookingResponse, SpaceCreate, SpaceResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coworking Space Booking API", version="1.0.0")


@app.get("/health", tags=["Monitoring"])
def health_check():
    return {"status": "healthy"}


@app.post("/spaces/", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED, tags=["Spaces"])
def create_space(space: SpaceCreate, db: Session = Depends(get_db)):
    existing = db.query(Space).filter(Space.name == space.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A space with this name already exists.")
    new_space = Space(**space.model_dump())
    db.add(new_space)
    db.commit()
    db.refresh(new_space)
    return new_space


@app.get("/spaces/", response_model=List[SpaceResponse], tags=["Spaces"])
def list_spaces(db: Session = Depends(get_db)):
    return db.query(Space).all()


@app.post("/bookings/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, tags=["Bookings"])
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    space = db.query(Space).filter(Space.id == booking.space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found.")

    # Overlap detection: (ExistingStart < NewEnd) AND (ExistingEnd > NewStart)
    conflict = (
        db.query(Booking)
        .filter(
            Booking.space_id == booking.space_id,
            Booking.start_time < booking.end_time,
            Booking.end_time > booking.start_time,
        )
        .first()
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Space is already booked for this time window.")

    new_booking = Booking(**booking.model_dump())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


@app.get("/bookings/", response_model=List[BookingResponse], tags=["Bookings"])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()
