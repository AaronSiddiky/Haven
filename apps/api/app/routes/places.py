from fastapi import APIRouter, Header, HTTPException
from typing import Optional

from app.core.errors import NotFoundError
from app.db.repositories import place_repository
from app.schemas.places import PlaceCreate, PlaceUpdate

router = APIRouter()


@router.get("")
def list_places(x_user_id: str = Header(...)):
    return place_repository.list_for_user(x_user_id)


@router.post("", status_code=201)
def create_place(body: PlaceCreate, x_user_id: str = Header(...)):
    return place_repository.create(x_user_id, body.model_dump())


@router.patch("/{place_id}")
def update_place(place_id: str, body: PlaceUpdate, x_user_id: str = Header(...)):
    place = place_repository.get(place_id)
    if not place or place.get("user_id") != x_user_id:
        raise NotFoundError("Place", place_id)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    return place_repository.update(place_id, updates)


@router.delete("/{place_id}", status_code=204)
def delete_place(place_id: str, x_user_id: str = Header(...)):
    place = place_repository.get(place_id)
    if not place or place.get("user_id") != x_user_id:
        raise NotFoundError("Place", place_id)
    place_repository.delete(place_id)
