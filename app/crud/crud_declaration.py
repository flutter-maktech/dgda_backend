import random
from typing import List, Optional
from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.declaration import Declaration
from app.schemas.declaration import DeclarationCreate, DeclarationUpdate


DEFAULT_SEED_DECLARATIONS = [
    {
        "reference_code": "DEC-2024-08412",
        "title": "Équipements Électroniques & Matériel IT",
        "type": "Importation Maritime",
        "location": "Port de Matadi",
        "status": "validated",
        "hs_code": "8471.30.00",
        "container_teu": "2 x 40' HQ",
        "estimated_duty_usd": "$ 4,850.00",
        "good_description": "Serveurs, unités centrales et ordinateurs portables pour entreprise.",
    },
    {
        "reference_code": "EXP-2024-03190",
        "title": "Concentrés Miniers & Produits d'Exportation",
        "type": "Exportation",
        "location": "Kinshasa Siège",
        "status": "inProgress",
        "hs_code": "2603.00.00",
        "container_teu": "4 x 20'",
        "estimated_duty_usd": "$ 12,400.00",
        "good_description": "Cargaison de concentrés de cuivre certifiée conforme.",
    },
    {
        "reference_code": "TR-2024-01254",
        "title": "Transit Régional de Marchandises Manufacturées",
        "type": "Transit T1 SADC",
        "location": "Kasumbalesa",
        "status": "pending",
        "hs_code": "8704.21.00",
        "container_teu": "1 x 40'",
        "estimated_duty_usd": "$ 1,950.00",
        "good_description": "Matériel de construction et outillage industriel en transit corridor sud.",
    },
    {
        "reference_code": "DEC-2024-09941",
        "title": "Pièces Détachées Aéronautiques",
        "type": "Importation Express",
        "location": "Aéroport N'djili",
        "status": "rejected",
        "hs_code": "8803.30.00",
        "container_teu": "Colis Aérien Fret",
        "estimated_duty_usd": "$ 820.00",
        "good_description": "Composants aéronautiques — document de conformité manquant.",
    },
]


async def seed_user_initial_declarations(db: AsyncSession, user_id: int) -> None:
    """Seed initial 4 realistic DGDA declarations if user has none."""
    for item in DEFAULT_SEED_DECLARATIONS:
        # Create unique reference code per user if needed
        ref = item["reference_code"]
        existing = await db.execute(select(Declaration).where(Declaration.reference_code == ref))
        if existing.scalars().first():
            # If standard reference exists for another user, prefix with user id
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
    # Check if user has any declarations; if 0, seed default ones
    count_query = select(Declaration).where(Declaration.user_id == user_id)
    count_result = await db.execute(count_query)
    if not count_result.scalars().first():
        await seed_user_initial_declarations(db, user_id)

    query = select(Declaration).where(Declaration.user_id == user_id)

    if status and status.lower() not in ["all", ""]:
        # Normalize status (support 'in_progress' and 'inProgress')
        normalized_status = "inProgress" if status.lower() in ["inprogress", "in_progress"] else status
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
        # Auto-generate reference code e.g. DEC-2026-XXXXX
        prefix = "DEC" if "import" in declaration_in.type.lower() else "EXP" if "export" in declaration_in.type.lower() else "TR"
        ref_code = f"{prefix}-2026-{random.randint(10000, 99999)}"

    # Check uniqueness
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
    await db.flush()
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

    # Normalize aliases
    if "hsCode" in raw_data and raw_data["hsCode"]:
        db_obj.hs_code = raw_data["hsCode"]
    if "containerTeu" in raw_data and raw_data["containerTeu"]:
        db_obj.container_teu = raw_data["containerTeu"]
    if "estimatedDutyUsd" in raw_data and raw_data["estimatedDutyUsd"]:
        db_obj.estimated_duty_usd = raw_data["estimatedDutyUsd"]
    if "goodDescription" in raw_data and raw_data["goodDescription"]:
        db_obj.good_description = raw_data["goodDescription"]

    await db.flush()
    await db.refresh(db_obj)
    return db_obj


async def delete_declaration(db: AsyncSession, db_obj: Declaration) -> None:
    """Delete a declaration."""
    await db.delete(db_obj)
    await db.flush()
