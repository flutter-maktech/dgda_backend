from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DeclarationBase(BaseModel):
    title: Optional[str] = None
    type: str = "Import"
    location: str = "Port de Matadi"
    status: str = "pending"
    hs_code: Optional[str] = None
    hsCode: Optional[str] = None
    container_teu: Optional[str] = None
    containerTeu: Optional[str] = None
    estimated_duty_usd: Optional[str] = None
    estimatedDutyUsd: Optional[str] = None
    good_description: Optional[str] = None
    goodDescription: Optional[str] = None

    def get_hs_code(self) -> str:
        return self.hs_code or self.hsCode or ""

    def get_container_teu(self) -> str:
        return self.container_teu or self.containerTeu or ""

    def get_estimated_duty_usd(self) -> str:
        return self.estimated_duty_usd or self.estimatedDutyUsd or ""

    def get_good_description(self) -> str:
        return self.good_description or self.goodDescription or ""


class DeclarationCreate(DeclarationBase):
    reference_code: Optional[str] = None
    referenceCode: Optional[str] = None


class DeclarationUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    hs_code: Optional[str] = None
    hsCode: Optional[str] = None
    container_teu: Optional[str] = None
    containerTeu: Optional[str] = None
    estimated_duty_usd: Optional[str] = None
    estimatedDutyUsd: Optional[str] = None
    good_description: Optional[str] = None
    goodDescription: Optional[str] = None


class DeclarationResponse(BaseModel):
    id: int
    user_id: int
    reference_code: str
    referenceCode: Optional[str] = None
    title: str
    type: str
    location: str
    status: str
    hs_code: Optional[str] = None
    hsCode: Optional[str] = None
    container_teu: Optional[str] = None
    containerTeu: Optional[str] = None
    estimated_duty_usd: Optional[str] = None
    estimatedDutyUsd: Optional[str] = None
    good_description: Optional[str] = None
    goodDescription: Optional[str] = None
    date: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_custom(cls, obj) -> "DeclarationResponse":
        months = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        created: datetime = obj.created_at
        month_name = months[created.month - 1] if 1 <= created.month <= 12 else ""
        formatted_date = f"{created.day} {month_name} {created.year}"

        return cls(
            id=obj.id,
            user_id=obj.user_id,
            reference_code=obj.reference_code,
            referenceCode=obj.reference_code,
            title=obj.title,
            type=obj.type,
            location=obj.location,
            status=obj.status,
            hs_code=obj.hs_code,
            hsCode=obj.hs_code,
            container_teu=obj.container_teu,
            containerTeu=obj.container_teu,
            estimated_duty_usd=obj.estimated_duty_usd,
            estimatedDutyUsd=obj.estimated_duty_usd,
            good_description=obj.good_description,
            goodDescription=obj.good_description,
            date=formatted_date,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
