from fastapi import APIRouter, Header

from app.core.errors import NotFoundError
from app.db.repositories import user_repository
from app.schemas.contacts import ContactCreate, ContactUpdate

router = APIRouter()


@router.get("")
def list_contacts(x_user_id: str = Header(...)):
    return user_repository.get_contacts(x_user_id)


@router.post("", status_code=201)
def create_contact(body: ContactCreate, x_user_id: str = Header(...)):
    return user_repository.create_contact(x_user_id, body.model_dump())


@router.patch("/{contact_id}")
def update_contact(contact_id: str, body: ContactUpdate, x_user_id: str = Header(...)):
    contact = user_repository.get_contact(contact_id)
    if not contact or contact.get("user_id") != x_user_id:
        raise NotFoundError("Contact", contact_id)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    return user_repository.update_contact(contact_id, updates)


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: str, x_user_id: str = Header(...)):
    contact = user_repository.get_contact(contact_id)
    if not contact or contact.get("user_id") != x_user_id:
        raise NotFoundError("Contact", contact_id)
    user_repository.delete_contact(contact_id)
