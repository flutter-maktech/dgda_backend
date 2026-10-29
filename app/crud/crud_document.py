from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customs_document import CustomsDocument
from app.schemas.customs_document import CustomsDocumentCreate, CustomsDocumentUpdate


INITIAL_DOCUMENTS = [
    {
        "title": "Code des Douanes de la RDC (Loi n° 10/002 du 20 août 2010)",
        "category": "Tariffs & Codes",
        "format": "PDF",
        "file_size": "8.4 MB",
        "date": "Jan 2024",
        "download_url": "https://dgda-backend.maktechapp.cloud/public/docs/code_des_douanes_rdc.pdf",
        "image_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=300",
        "description": "Texte législatif fondamental régissant l'ensemble des opérations douanières, droits et accises en République Démocratique du Congo."
    },
    {
        "title": "Tarif des Droits et Taxes à l’Importation (Nomenclature SH 2024)",
        "category": "Tariffs & Codes",
        "format": "PDF",
        "file_size": "6.2 MB",
        "date": "Août 2024",
        "download_url": "https://dgda-backend.maktechapp.cloud/public/docs/tarif_douanier_sh_2024.pdf",
        "image_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=300",
        "description": "Nomenclature tarifaire et statistique combinée reprenant les taux des droits de douane, TVA et redevances applicables."
    },
    {
        "title": "Guide Officiel de Dédouanement Import / Export",
        "category": "Procedures & Forms",
        "format": "PDF",
        "file_size": "3.8 MB",
        "date": "Sept 2024",
        "download_url": "https://dgda-backend.maktechapp.cloud/public/docs/guide_dedouanement_2024.pdf",
        "image_url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?w=300",
        "description": "Manuel complet détaillant les formalités préalables à l'embarquement (FERI, DPI), le Guichet Unique SEGUCE et SydoniaWorld."
    },
    {
        "title": "Déclaration Unique de Douane (DUD / DAU) — Formulaire & Guide",
        "category": "Procedures & Forms",
        "format": "PDF",
        "file_size": "1.9 MB",
        "date": "Juil 2024",
        "download_url": "https://dgda-backend.maktechapp.cloud/public/docs/formulaire_dud_dau.pdf",
        "image_url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=300",
        "description": "Spécimen officiel du Document Administratif Unique (DAU) avec les instructions de remplissage case par case."
    },
    {
        "title": "Régime de Transit T1 — Corridor Régional SADC / COMESA",
        "category": "Bilateral Treaties",
        "format": "PDF",
        "file_size": "2.5 MB",
        "date": "Juin 2024",
        "download_url": "https://dgda-backend.maktechapp.cloud/public/docs/regime_transit_t1_sadc.pdf",
        "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=300",
        "description": "Directives relatives aux déclarations sous acquit-à-caution T1, garanties bancaires et scellement électronique DGDA."
    },
    {
        "title": "Manuel des Procédures Opérationnelles SYDONIA World",
        "category": "Procedures & Forms",
        "format": "PDF",
        "file_size": "4.1 MB",
        "date": "Mai 2024",
        "download_url": "https://dgda-backend.maktechapp.cloud/public/docs/manuel_sydoniaworld_dgda.pdf",
        "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=300",
        "description": "Guide technique d'utilisation de la plateforme SydoniaWorld pour les Commissionnaires en Douane Agréés (CDA)."
    },
    {
        "title": "Guide Officiel des Exonérations Fiscales et Douanières ANAPI",
        "category": "Exemptions",
        "format": "PDF",
        "file_size": "2.8 MB",
        "date": "Mars 2024",
        "download_url": "https://dgda-backend.maktechapp.cloud/public/docs/guide_exonerations_anapi.pdf",
        "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300",
        "description": "Modalités d'octroi des franchises et régimes privilégiés du Code des Investissements et du Code Minier."
    },
]


async def get_documents(
    db: AsyncSession,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> List[CustomsDocument]:
    query = select(CustomsDocument)

    if category and category.lower() != "all":
        query = query.where(CustomsDocument.category.ilike(f"%{category}%"))

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.where(
            (CustomsDocument.title.ilike(search_filter)) |
            (CustomsDocument.description.ilike(search_filter))
        )

    query = query.order_by(CustomsDocument.id.asc())
    result = await db.execute(query)
    docs = list(result.scalars().all())

    # Auto-seed if database is empty
    if not docs and not category and not search:
        for item in INITIAL_DOCUMENTS:
            doc = CustomsDocument(**item)
            db.add(doc)
        await db.commit()

        # Re-fetch seeded documents
        refreshed = await db.execute(query)
        docs = list(refreshed.scalars().all())

    return docs


async def get_document_by_id(db: AsyncSession, document_id: int) -> Optional[CustomsDocument]:
    result = await db.execute(select(CustomsDocument).where(CustomsDocument.id == document_id))
    return result.scalar_one_or_none()


async def create_document(db: AsyncSession, doc_in: CustomsDocumentCreate) -> CustomsDocument:
    db_obj = CustomsDocument(**doc_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_document(
    db: AsyncSession, document_id: int, doc_in: CustomsDocumentUpdate
) -> Optional[CustomsDocument]:
    db_obj = await get_document_by_id(db, document_id=document_id)
    if not db_obj:
        return None
    update_data = doc_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_document(db: AsyncSession, document_id: int) -> bool:
    db_obj = await get_document_by_id(db, document_id=document_id)
    if not db_obj:
        return False
    await db.delete(db_obj)
    await db.commit()
    return True
