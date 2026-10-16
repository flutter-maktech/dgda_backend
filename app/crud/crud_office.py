from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customs_office import CustomsOffice


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
        "working_hours": "06h00 - 22h00 (Service continu)",
        "station_code": "CD-STN-512",
        "region": "Nord-Kivu",
        "authority": "Inspecteur Chef de Bureau",
        "juxtaposed_post": "Poste Frontalier Goma - Gisenyi",
        "tags": "Import,Export,Transit,Border Post,COMESA",
        "phone": "+243 85 444 7890",
        "is_open": True,
        "latitude": -1.6833,
        "longitude": 29.2333,
    },
    {
        "code": "[CDBOM]",
        "name": "Port Maritime de Boma",
        "subtitle": "Port de Débarcadère & Véhicules d'Occasion",
        "office_location": "Enceinte Portuaire de Boma, Kongo Central",
        "working_hours": "07h30 - 18h00",
        "station_code": "CD-STN-418",
        "region": "Kongo Central",
        "authority": "Inspecteur Principal",
        "juxtaposed_post": "Port de Boma et Parcs à Conteneurs",
        "tags": "Import,Maritime Port,Véhicules,Vrac",
        "phone": "+243 81 333 9988",
        "is_open": True,
        "latitude": -5.8500,
        "longitude": 13.0500,
    },
    {
        "code": "[CDLUF]",
        "name": "Poste Frontalier de Lufu",
        "subtitle": "Marché Transfrontalier RDC-Angola",
        "office_location": "Zone Douanière de Lufu, Territoire de Songololo",
        "working_hours": "07h00 - 19h00",
        "station_code": "CD-STN-435",
        "region": "Kongo Central",
        "authority": "Inspecteur Chef de Poste",
        "juxtaposed_post": "Poste Frontalier RDC - Luvo Angola",
        "tags": "Commerce Transfrontalier,Import,Export",
        "phone": "+243 82 111 2233",
        "is_open": False,
        "latitude": -5.9167,
        "longitude": 14.2833,
    },
]


async def get_offices(
    db: AsyncSession,
    region: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[CustomsOffice]:
    query = select(CustomsOffice)

    if region and region.lower() != "all" and region.lower() != "all regions":
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
