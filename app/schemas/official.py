from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class GovernmentOfficialBase(BaseModel):
    badge_text: str
    role_title: str
    honorific: str
    name: str
    photo_path: Optional[str] = None
    photo_url: Optional[str] = None
    biography: str
    responsibilities: List[str] = []
    mandate_period: str
    cabinet_office: Optional[str] = None
    official_website: Optional[str] = None
    display_order: Optional[int] = 0


class GovernmentOfficialCreate(GovernmentOfficialBase):
    id: str


class GovernmentOfficialUpdate(BaseModel):
    badge_text: Optional[str] = None
    role_title: Optional[str] = None
    honorific: Optional[str] = None
    name: Optional[str] = None
    photo_path: Optional[str] = None
    photo_url: Optional[str] = None
    biography: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    mandate_period: Optional[str] = None
    cabinet_office: Optional[str] = None
    official_website: Optional[str] = None
    display_order: Optional[int] = None


class GovernmentOfficialResponse(GovernmentOfficialBase):
    id: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ManagementMemberBase(BaseModel):
    full_name: str
    role_or_title: str
    subtitle: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    quote: Optional[str] = None
    asset_path: Optional[str] = None
    photo_url: Optional[str] = None
    source_reference: Optional[str] = None
    official_email: Optional[str] = "contact@douane.gouv.cd"
    official_phone: Optional[str] = "+243 82 192 0215"
    official_source_url: Optional[str] = "https://douane.gouv.cd/dgda/services/"
    category: str
    filter_tag: Optional[str] = None
    is_dg: Optional[bool] = False
    is_dga: Optional[bool] = False
    display_order: Optional[int] = 0


class ManagementMemberCreate(ManagementMemberBase):
    id: str


class ManagementMemberUpdate(BaseModel):
    full_name: Optional[str] = None
    role_or_title: Optional[str] = None
    subtitle: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    quote: Optional[str] = None
    asset_path: Optional[str] = None
    photo_url: Optional[str] = None
    source_reference: Optional[str] = None
    official_email: Optional[str] = None
    official_phone: Optional[str] = None
    official_source_url: Optional[str] = None
    category: Optional[str] = None
    filter_tag: Optional[str] = None
    is_dg: Optional[bool] = None
    is_dga: Optional[bool] = None
    display_order: Optional[int] = None


class ManagementMemberResponse(ManagementMemberBase):
    id: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
