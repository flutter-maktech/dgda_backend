from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    description: Optional[str] = "Signalement de données erronées"
    detailed_description: str
    reporting_user: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None


class ReportUpdate(BaseModel):
    status: Optional[str] = None  # PENDING, UNDER_REVIEW, RESOLVED
    admin_notes: Optional[str] = None
    description: Optional[str] = None
    detailed_description: Optional[str] = None


class ReportResponse(BaseModel):
    id: str
    report_code: str
    reporting_user: str
    email: Optional[str] = ""
    telephone: Optional[str] = ""
    description: str
    detailed_description: str
    status: str
    admin_notes: Optional[str] = ""
    submission_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Convenience properties / aliases for Admin Dashboard compatibility
    @property
    def reportCode(self) -> str:
        return self.report_code

    @property
    def reportingUser(self) -> str:
        return self.reporting_user

    @property
    def detailedDescription(self) -> str:
        return self.detailed_description

    @property
    def adminNotes(self) -> Optional[str]:
        return self.admin_notes

    @property
    def date(self) -> Optional[str]:
        return self.submission_date

    model_config = ConfigDict(from_attributes=True)
