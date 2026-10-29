import random
from typing import List, Optional
from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.declaration import Declaration
from app.schemas.declaration import DeclarationCreate, DeclarationUpdate


DEFAULT_SEED_DECLARATIONS = [
    {
        "reference_code": "DEC-2026-004812",
        "title": "Industrial Heavy Mining Drills & Hydraulic Replacement Parts",
        "type": "Import",
        "location": "Kasumbalesa Border Control",
        "status": "pending",
        "hs_code": "8430.49.00",
        "container_teu": "2 x 40' HQ",
        "estimated_duty_usd": "$ 285,400.00",
        "good_description": "Importer: Kamoto Copper Company (KCC) • Broker: Kabuya Marcel Logistics (NIF: A0812934B). BIVAC Certificate inspection attached.",
    },
    {
        "reference_code": "DEC-2026-004809",
        "title": "Refined Grade A Copper Cathodes (Bulk Freight)",
        "type": "Export",
        "location": "Kolwezi Customs Terminal",
        "status": "validated",
        "hs_code": "7403.11.00",
        "container_teu": "8 x 20'",
        "estimated_duty_usd": "$ 1,450,000.00",
        "good_description": "Importer: Tenke Fungurume Mining (TFM) • Broker: Trans-Katanga Freight SARL (NIF: A0948372C).",
    },
    {
        "reference_code": "DEC-2026-004795",
        "title": "Essential Antibiotics, Vaccines & Medical Diagnostic Kits",
        "type": "Import",
        "location": "N'djili International Airport Fret",
        "status": "validated",
        "hs_code": "3004.90.00",
        "container_teu": "Air Cargo Pallets",
        "estimated_duty_usd": "Exempt / Duty Free",
        "good_description": "Importer: Pharmagros Kinshasa • Broker: Global Transit Congo (NIF: A0732859D).",
    },
    {
        "reference_code": "DEC-2026-004780",
        "title": "High-Voltage Electrical Transformers & Substation Cables",
        "type": "Transit",
        "location": "Matadi Seaport Terminal",
        "status": "inProgress",
        "hs_code": "8504.23.00",
        "container_teu": "4 x 40'",
        "estimated_duty_usd": "Exempt / Transit Bond T1",
        "good_description": "Importer: Great Lakes Energy Consortium • Broker: Congo Corridor Logistics (NIF: A0548232E).",
    },
    {
        "reference_code": "DEC-2026-004762",
        "title": "Commercial Used Heavy Trucks & Earth-Moving Machinery",
        "type": "Import",
        "location": "Boma Maritime Port",
        "status": "rejected",
        "hs_code": "8704.23.00",
        "container_teu": "Ro-Ro Vehicle Units",
        "estimated_duty_usd": "$ 42,600.00",
        "good_description": "Importer: Congo Mining Fleet SA • Non-compliant manufacture year >10 years (Decree 12/041).",
    },
]


async def seed_user_initial_declarations(db: AsyncSession, user_id: int) -> None:
    """Seed initial realistic DGDA declarations if user has none."""
    for item in DEFAULT_SEED_DECLARATIONS:
        ref = item["reference_code"]
        existing = await db.execute(select(Declaration).where(Declaration.reference_code == ref))
        if existing.scalars().first():
            ref = f"{item['reference_code'].split('-')[0]}-{user_id}-{random.randint(1000, 9999)}"

        decl = Declaration(
            user_id=user_id,
            reference_code=ref,
            title=item["title"],
            type=item["type"],
            location=item["location"],
            status=item["status"],
            hs_code=item["hs_code"],
            container_teu=item["container_teu"],
            estimated_duty_usd=item["estimated_duty_usd"],
            good_description=item["good_description"],
        )
        db.add(decl)
    await db.commit()


async def get_user_declarations(
    db: AsyncSession,
    user_id: int,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Declaration]:
    """Retrieve declarations for a specific user with optional status filter and search query."""
    count_query = select(Declaration).where(Declaration.user_id == user_id)
    count_result = await db.execute(count_query)
    if not count_result.scalars().first():
        await seed_user_initial_declarations(db, user_id)

    query = select(Declaration).where(Declaration.user_id == user_id)

    if status and status.lower() not in ["all", ""]:
        normalized_status = "inProgress" if status.lower() in ["inprogress", "in_progress", "under inspection"] else status
        query = query.where(Declaration.status == normalized_status)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Declaration.reference_code.ilike(term),
                Declaration.title.ilike(term),
                Declaration.hs_code.ilike(term),
                Declaration.location.ilike(term),
                Declaration.good_description.ilike(term),
            )
        )

    query = query.order_by(desc(Declaration.created_at))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_all_declarations(
    db: AsyncSession,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Declaration]:
    """Retrieve all declarations across all users for administrative review."""
    count_query = select(Declaration)
    count_result = await db.execute(count_query)
    if not count_result.scalars().first():
        # Seed system defaults under admin user ID 1
        await seed_user_initial_declarations(db, 1)

    query = select(Declaration)

    if status and status.lower() not in ["all", ""]:
        normalized_status = "inProgress" if status.lower() in ["inprogress", "in_progress", "under inspection"] else status
        query = query.where(Declaration.status == normalized_status)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Declaration.reference_code.ilike(term),
                Declaration.title.ilike(term),
                Declaration.hs_code.ilike(term),
                Declaration.location.ilike(term),
                Declaration.good_description.ilike(term),
            )
        )

    query = query.order_by(desc(Declaration.created_at))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_declaration_by_id(
    db: AsyncSession, declaration_id: int, user_id: Optional[int] = None
) -> Optional[Declaration]:
    """Retrieve declaration by its primary key."""
    query = select(Declaration).where(Declaration.id == declaration_id)
    if user_id:
        query = query.where(Declaration.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def create_declaration(
    db: AsyncSession, declaration_in: DeclarationCreate, user_id: int
) -> Declaration:
    """Create a new declaration for the user."""
    ref_code = declaration_in.reference_code or declaration_in.referenceCode
    if not ref_code or not ref_code.strip():
        prefix = "DEC" if "import" in declaration_in.type.lower() else "EXP" if "export" in declaration_in.type.lower() else "TR"
        ref_code = f"{prefix}-2026-{random.randint(10000, 99999)}"

    existing = await db.execute(select(Declaration).where(Declaration.reference_code == ref_code))
    if existing.scalars().first():
        ref_code = f"{ref_code}-{random.randint(10, 99)}"

    title = declaration_in.title
    if not title or not title.strip():
        desc_text = declaration_in.get_good_description()
        title = desc_text if desc_text else f"Déclaration {declaration_in.type} - {declaration_in.location}"

    db_obj = Declaration(
        user_id=user_id,
        reference_code=ref_code,
        title=title,
        type=declaration_in.type,
        location=declaration_in.location,
        status=declaration_in.status or "pending",
        hs_code=declaration_in.get_hs_code(),
        container_teu=declaration_in.get_container_teu(),
        estimated_duty_usd=declaration_in.get_estimated_duty_usd(),
        good_description=declaration_in.get_good_description(),
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_declaration(
    db: AsyncSession, db_obj: Declaration, obj_in: DeclarationUpdate
) -> Declaration:
    """Update an existing declaration."""
    raw_data = obj_in.model_dump(exclude_unset=True)
    for field, value in raw_data.items():
        if hasattr(db_obj, field) and value is not None:
            setattr(db_obj, field, value)

    if "hsCode" in raw_data and raw_data["hsCode"]:
        db_obj.hs_code = raw_data["hsCode"]
    if "containerTeu" in raw_data and raw_data["containerTeu"]:
        db_obj.container_teu = raw_data["containerTeu"]
    if "estimatedDutyUsd" in raw_data and raw_data["estimatedDutyUsd"]:
        db_obj.estimated_duty_usd = raw_data["estimatedDutyUsd"]
    if "goodDescription" in raw_data and raw_data["goodDescription"]:
        db_obj.good_description = raw_data["goodDescription"]

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_declaration(db: AsyncSession, db_obj: Declaration) -> None:
    """Delete a declaration."""
    await db.delete(db_obj)
    await db.commit()
