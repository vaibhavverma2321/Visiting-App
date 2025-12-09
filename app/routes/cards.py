from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from dependencies import get_db, get_current_user
from sqlalchemy.orm import selectinload
from fastapi.responses import Response
import xml.etree.ElementTree as ET


router = APIRouter(prefix="/cards", tags=["Visiting Cards"])

@router.post("/")
def add_card(
    card: schemas.VisitingCardCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    new_card = models.VisitingCard(
        user_id=user.id,
        person_name=card.person_name,
        designation=card.designation,
        company_name=card.company_name,
        email=card.email,
        address=card.address,
        description=card.description
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    for number in card.phone_numbers:
        phone_obj = models.PhoneNumber(
            phone=number,
            card_id=new_card.id
        )
        db.add(phone_obj)

    db.commit()

    return {
        "message": "Visiting card saved successfully",
        "card_id": new_card.id
    }

@router.get("/")
def get_cards(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    cards = (
        db.query(models.VisitingCard)
        .options(selectinload(models.VisitingCard.phone_numbers))
        .filter(models.VisitingCard.user_id == user.id)
        .all()
    )

    return cards

from fastapi import HTTPException

# Get Single Card
@router.get("/{card_id}")
def get_card(
    card_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    card = (
        db.query(models.VisitingCard)
        .options(selectinload(models.VisitingCard.phone_numbers))
        .filter(
            models.VisitingCard.id == card_id,
            models.VisitingCard.user_id == user.id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return card


# Update Card
@router.put("/{card_id}")
def update_card(
    card_id: int,
    updated_data: schemas.VisitingCardCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    card = db.query(models.VisitingCard).filter(
        models.VisitingCard.id == card_id,
        models.VisitingCard.user_id == user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Update main card fields
    card.person_name = updated_data.person_name
    card.designation = updated_data.designation
    card.company_name = updated_data.company_name
    card.email = updated_data.email
    card.address = updated_data.address
    card.description = updated_data.description

    # Clear old phone numbers and re-add new
    db.query(models.PhoneNumber).filter(
        models.PhoneNumber.card_id == card_id
    ).delete()

    for number in updated_data.phone_numbers:
        db.add(models.PhoneNumber(phone=number, card_id=card_id))

    db.commit()
    return {"message": "Card updated successfully"}


# Delete Card
@router.delete("/{card_id}")
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    card = db.query(models.VisitingCard).filter(
        models.VisitingCard.id == card_id,
        models.VisitingCard.user_id == user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    db.delete(card)
    db.commit()
    return {"message": "Card deleted successfully"}

@router.get("/download/{card_id}", response_class=Response)
def download_card_xml(
    card_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    card = (
        db.query(models.VisitingCard)
        .options(selectinload(models.VisitingCard.phone_numbers))
        .filter(
            models.VisitingCard.id == card_id,
            models.VisitingCard.user_id == user.id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Create XML structure
    card_xml = ET.Element("VisitingCard")

    ET.SubElement(card_xml, "PersonName").text = card.person_name
    ET.SubElement(card_xml, "Designation").text = card.designation
    ET.SubElement(card_xml, "CompanyName").text = card.company_name
    ET.SubElement(card_xml, "Email").text = card.email
    ET.SubElement(card_xml, "Address").text = card.address
    ET.SubElement(card_xml, "Description").text = card.description

    phones_element = ET.SubElement(card_xml, "PhoneNumbers")
    for number in card.phone_numbers:
        ET.SubElement(phones_element, "Phone").text = number.phone

    # Convert XML to string
    xml_string = ET.tostring(card_xml, encoding="utf-8")

    # Return XML as a downloadable file
    return Response(
        content=xml_string,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=card_{card_id}.xml"
        }
    )
