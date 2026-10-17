from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CompanyServiceSchema(BaseModel):
    title: str
    iconType: str = "customs"


class PartnerBase(BaseModel):
    name: str
    category: str = "Partners"  # Partners, Sponsors, Logistics, Banking, Insurance, etc.
    tier: str = "Official Partner"  # Principal Sponsor, Official Partner, Recommended Professional, etc.
    is_principal_sponsor: bool = False
    is_partner: bool = True  # True = Partner/Sponsor, False = Recommended Professional
    status: str = "Active"  # Active, Inactive

    logo_url: Optional[str] = None
    asset_path: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    role: Optional[str] = None
    tagline: Optional[str] = None
    headline: Optional[str] = None
    hero_subtitle: Optional[str] = None
    tags: List[str] = []
    about_text: Optional[str] = None
    services: List[Dict[str, Any]] = []
    slogan: Optional[str] = None

    is_official_badge: bool = True
    is_trusted_badge: bool = True
    display_order: int = 0


class PartnerCreate(PartnerBase):
    id: Optional[str] = None


class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    tier: Optional[str] = None
    is_principal_sponsor: Optional[bool] = None
    is_partner: Optional[bool] = None
    status: Optional[str] = None

    logo_url: Optional[str] = None
    asset_path: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    role: Optional[str] = None
    tagline: Optional[str] = None
    headline: Optional[str] = None
    hero_subtitle: Optional[str] = None
    tags: Optional[List[str]] = None
    about_text: Optional[str] = None
    services: Optional[List[Dict[str, Any]]] = None
    slogan: Optional[str] = None

    is_official_badge: Optional[bool] = None
    is_trusted_badge: Optional[bool] = None
    display_order: Optional[int] = None


class PartnerResponse(PartnerBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
