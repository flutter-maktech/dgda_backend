from app.crud.crud_user import (
    authenticate,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    get_users_list,
    update_user,
)
from app.crud.crud_declaration import (
    get_user_declarations,
    get_declaration_by_id,
    create_declaration,
    update_declaration,
    delete_declaration,
)
from app.crud.crud_calendar_event import (
    get_user_calendar_events,
    create_calendar_event,
    get_calendar_event_by_id,
    update_calendar_event,
    delete_calendar_event,
)

from app.crud.crud_faq import crud_faq
from app.crud.crud_report import crud_report
from app.crud.crud_content import crud_content
from app.crud.crud_support import crud_support

__all__ = [
    "get_user_by_id",
    "get_user_by_email",
    "get_user_by_username",
    "create_user",
    "authenticate",
    "update_user",
    "get_users_list",
    "create_otp",
    "verify_otp",
    "get_user_declarations",
    "get_declaration_by_id",
    "create_declaration",
    "update_declaration",
    "delete_declaration",
    "get_user_calendar_events",
    "create_calendar_event",
    "get_calendar_event_by_id",
    "update_calendar_event",
    "delete_calendar_event",
    "crud_faq",
    "crud_report",
    "crud_content",
    "crud_support",
]
