from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customs_office import CustomsOffice
from app.schemas.customs_office import CustomsOfficeCreate, CustomsOfficeUpdate


INITIAL_OFFICES = [
    {
        "code": "[CDMAT]",
        "name": "Port de Matadi",
        "subtitle": "Port Maritime Principal de la RDC",
        "office_location": "Matadi Port Customs Office, Kongo Central",
        "working_hours": "24/7 Commercial Corridors",
        "station_code": "CD-STN-421",
        "region": "Kongo Central",
        "authority": "Inspecteur Principal",
        "juxtaposed_post": "Port Fluvial et Maritime de Matadi",
        "tags": "Import,Export,Transit,Maritime Port,Conteneurs",
        "phone": "+243 81 234 5678",
        "is_open": True,
        "latitude": -5.8167,
        "longitude": 13.4500,
    },
    {
        "code": "[CDKAS]",
        "name": "Poste Frontalier de Kasumbalesa",
        "subtitle": "Poste Juxtaposé RDC-Zambie (Corridor Sud)",
        "office_location": "Kasumbalesa Border Control Area, Haut-Katanga",
        "working_hours": "24/7 Commercial Corridors",
        "station_code": "CD-STN-804",
        "region": "Haut-Katanga",
        "authority": "Directeur Provincial",
        "juxtaposed_post": "Poste Frontalier Juxtaposé DRC-Zambia, Kasumbalesa",
        "tags": "Import,Export,Transit,Border Post,SADC",
        "phone": "+243 82 987 6543",
        "is_open": True,
        "latitude": -12.2564,
        "longitude": 27.8014,
    },
    {
        "code": "[CDNDJ]",
        "name": "Aéroport International de N'djili",
        "subtitle": "Direction du Fret Aérien & Passagers Kinshasa",
        "office_location": "Aéroport de N'djili, Terminal Fret DGDA, Kinshasa",
        "working_hours": "24/7 Fret et Dédouanement Express",
        "station_code": "CD-STN-101",
        "region": "Kinshasa",
        "authority": "Inspecteur Principal",
        "juxtaposed_post": "Aéroport International de N'djili (FIH)",
        "tags": "Import,Export,Air Cargo,Express Courier",
        "phone": "+243 81 555 1234",
        "is_open": True,
        "latitude": -4.3858,
        "longitude": 15.4444,
    },
    {
        "code": "[CDGOM]",
        "name": "Bureau de Douane de Goma",
        "subtitle": "Poste Frontalier RDC-Rwanda (Grande Barrière)",
        "office_location": "Grande Barrière, Boulevard Kanyamuhanga, Goma",
        "working_hours": "06:00 - 22:00 (7j/7)",
        "station_code": "CD-STN-305",
        "region": "Nord-Kivu",
        "authority": "Chef de Bureau Principal",
        "juxtaposed_post": "Poste Frontière Grande Barrière (Rubavu / Goma)",
        "tags": "Import,Export,Cross-Border Trade,Passagers",
        "phone": "+243 99 876 5432",
        "is_open": True,
        "latitude": -1.6917,
        "longitude": 29.2394,
    },
    {
        "code": "[CDKOL]",
        "name": "Terminal Douanier de Kolwezi",
        "subtitle": "Centre Minier et Logistique du Lualaba",
        "office_location": "Zone Industrielle de Musompo, Kolwezi, Lualaba",
        "working_hours": "07:30 - 18:00 (Lun - Sam)",
        "station_code": "CD-STN-612",
        "region": "Lualaba",
        "authority": "Directeur Provincial Adjoint",
        "juxtaposed_post": "Centre de Négoce de Musompo",
        "tags": "Export Minier,Cobalt,Cuivre,Transit Ferroviaire",
        "phone": "+243 85 432 1098",
        "is_open": True,
        "latitude": -10.7167,
        "longitude": 25.4667,
    },
    {
        "code": "[CDBOM]",
        "name": "Port Maritime de Boma",
        "subtitle": "Débarquement Véhicules d'Occasion et Marchandises Diverses",
        "office_location": "Quai Maritime de Boma, Kongo Central",
        "working_hours": "08:00 - 17:00 (Lun - Ven)",
        "station_code": "CD-STN-410",
        "region": "Kongo Central",
        "authority": "Inspecteur de Division",
        "juxtaposed_post": "Port de Boma (ONATRA)",
        "tags": "Importation Véhicules,Roulier,Conteneurs",
        "phone": "+243 81 777 8899",
        "is_open": False,
        "latitude": -5.8500,
        "longitude": 13.0500,
    },
]


async def get_offices(
    db: AsyncSession,
    region: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[CustomsOffice]:
    query = select(CustomsOffice)

    if region and region.lower() != "all":
        query = query.where(CustomsOffice.region.ilike(f"%{region}%"))

    if status and status.lower() != "all":
        if status.lower() in ("open", "ouvert"):
            query = query.where(CustomsOffice.is_open.is_(True))
        elif status.lower() in ("closed", "ferme", "fermé"):
            query = query.where(CustomsOffice.is_open.is_(False))

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.where(
            (CustomsOffice.name.ilike(search_filter)) |
            (CustomsOffice.code.ilike(search_filter)) |
            (CustomsOffice.office_location.ilike(search_filter)) |
            (CustomsOffice.station_code.ilike(search_filter))
        )

    query = query.order_by(CustomsOffice.id.asc())
    result = await db.execute(query)
    offices = list(result.scalars().all())

    # Auto-seed if database is empty
    if not offices and not region and not status and not search:
        for item in INITIAL_OFFICES:
            office = CustomsOffice(**item)
            db.add(office)
        await db.commit()

        # Re-fetch seeded offices
        refreshed = await db.execute(query)
        offices = list(refreshed.scalars().all())

    return offices


async def get_office_by_id(db: AsyncSession, office_id: int) -> Optional[CustomsOffice]:
    result = await db.execute(select(CustomsOffice).where(CustomsOffice.id == office_id))
    return result.scalar_one_or_none()


async def create_office(db: AsyncSession, office_in: CustomsOfficeCreate) -> CustomsOffice:
    db_obj = CustomsOffice(**office_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_office(
    db: AsyncSession, office_id: int, office_in: CustomsOfficeUpdate
) -> Optional[CustomsOffice]:
    db_obj = await get_office_by_id(db, office_id=office_id)
    if not db_obj:
        return None
    update_data = office_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_office(db: AsyncSession, office_id: int) -> bool:
    db_obj = await get_office_by_id(db, office_id=office_id)
    if not db_obj:
        return False
    await db.delete(db_obj)
    await db.commit()
    return True
