from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.news_article import NewsArticle
from app.schemas.news_article import NewsArticleCreate, NewsArticleUpdate

INITIAL_NEWS = [
    {
        "title": "Modernisation du Système Douanier SYDONIA World",
        "subtitle": "Déploiement des nouveaux modules d'interconnexion pour accélérer le traitement des déclarations en ligne.",
        "content": "La Direction Générale des Douanes et Accises (DGDA) annonce le déploiement national des nouveaux modules d'interconnexion SYDONIA World. Ce projet stratégique vise la dématérialisation totale des déclarations en douane et l'automatisation du bon à enlever (BAE), réduisant le délai moyen de passage portuaire de 72h à moins de 24h.",
        "date": "28/08/2024",
        "category": "RÉFORMES",
        "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400",
        "pdf_url": "https://dgda-backend.maktechapp.cloud/public/docs/manuel_sydonia_world.pdf",
        "is_featured": True,
    },
    {
        "title": "Mise en application du Tarif Douanier Révisé OHADA & SH",
        "subtitle": "Le Ministère des Finances et la DGDA publient les taux révisés applicables aux marchandises importées.",
        "content": "Conformément aux directives de l'Organisation Mondiale des Douanes (OMD) et aux engagements régionaux OHADA/SADC, la DGDA publie la version 2024 de la nomenclature tarifaire et statistique. Les opérateurs économiques sont invités à mettre à jour leurs codes SH dans le système avant le 1er novembre.",
        "date": "15/08/2024",
        "category": "RÉGLEMENTATION",
        "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400",
        "pdf_url": "https://dgda-backend.maktechapp.cloud/public/docs/tarif_douanier_sh_2024.pdf",
        "is_featured": True,
    },
    {
        "title": "Renforcement du Contrôle au Guichet Unique de Kasumbalesa",
        "subtitle": "Optimisation de la fluidité du trafic lourd et réduction des temps d'attente sur le corridor sud.",
        "content": "Une délégation de haut niveau de la DGDA a inspecté le poste frontalier juxtaposé de Kasumbalesa. Des mesures d'urgence incluant l'extension des plages horaires et le doublement des couloirs de pesage ont été validées pour fluidifier le flux de camions miniers vers la Zambie.",
        "date": "02/08/2024",
        "category": "CORRIDORS",
        "image_url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?w=400",
        "pdf_url": "https://dgda-backend.maktechapp.cloud/public/docs/guide_dedouanement_2024.pdf",
        "is_featured": False,
    },
    {
        "title": "Lutte contre la Fraude et Déclarations Électroniques",
        "subtitle": "Sensibilisation des commissionnaires en douane agréés aux nouvelles obligations de traçabilité.",
        "content": "La Direction de la Lutte contre la Fraude douanière rappelle l'obligation stricte d'adjoindre le numéro d'identification fiscale (NIF) valide et les pièces justificatives numérisées à toute déclaration en douane sous peine de sanctions pécuniaires immédiates.",
        "date": "22/07/2024",
        "category": "COMMUNIQUÉ",
        "image_url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=400",
        "pdf_url": "https://dgda-backend.maktechapp.cloud/public/docs/formulaire_dud_dau.pdf",
        "is_featured": False,
    },
    {
        "title": "Partenariat Stratégique avec les Banques Commerciales",
        "subtitle": "Intégration du paiement électronique direct des droits de douane pour une sécurisation optimale des recettes.",
        "content": "La DGDA et l'Association Congolaise des Banques (ACB) ont signé un protocole d'accord d'interopérabilité permettant le règlement instantané des avis de mise en recouvrement (AMR) via les plateformes de banque en ligne sécurisées.",
        "date": "10/07/2024",
        "category": "FINANCES",
        "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400",
        "pdf_url": "https://dgda-backend.maktechapp.cloud/public/docs/regime_transit_t1_sadc.pdf",
        "is_featured": False,
    },
    {
        "title": "Numérisation des Procédures au Port Maritime de Matadi",
        "subtitle": "Mise en service des scanners mobiles à rayons X de dernière génération pour conteneurs.",
        "content": "Deux nouveaux portiques d'inspection non-intrusive ont été inaugurés au port de Matadi en présence des autorités provinciales du Kongo Central, garantissant une détection rapide sans rupture de charge.",
        "date": "25/06/2024",
        "category": "OPÉRATIONS",
        "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400",
        "pdf_url": "https://dgda-backend.maktechapp.cloud/public/docs/code_des_douanes_rdc.pdf",
        "is_featured": False,
    },
]

class CRUDNews:
    async def get_multi(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[NewsArticle]:
        stmt = select(NewsArticle)

        if category and category.lower() != "all":
            stmt = stmt.where(NewsArticle.category.ilike(f"%{category}%"))

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (NewsArticle.title.ilike(search_pattern))
                | (NewsArticle.subtitle.ilike(search_pattern))
                | (NewsArticle.category.ilike(search_pattern))
            )

        stmt = stmt.order_by(NewsArticle.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        # Auto-seed if empty
        if not items and not category and not search:
            for item_data in INITIAL_NEWS:
                article = NewsArticle(**item_data)
                db.add(article)
            await db.commit()

            result = await db.execute(select(NewsArticle).order_by(NewsArticle.created_at.desc()))
            items = list(result.scalars().all())
        else:
            # Backfill pdf_url for existing items if missing
            updated = False
            for item in items:
                if not getattr(item, "pdf_url", None):
                    for init_item in INITIAL_NEWS:
                        if init_item["title"] == item.title:
                            item.pdf_url = init_item["pdf_url"]
                            db.add(item)
                            updated = True
                            break
            if updated:
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()

        return items

    async def get(self, db: AsyncSession, id: str) -> Optional[NewsArticle]:
        stmt = select(NewsArticle).where(NewsArticle.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: NewsArticleCreate) -> NewsArticle:
        item_data = obj_in.model_dump()
        if "id" not in item_data or not item_data["id"]:
            item_data["id"] = str(uuid.uuid4())
        db_obj = NewsArticle(**item_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: NewsArticle, obj_in: NewsArticleUpdate
    ) -> NewsArticle:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> bool:
        db_obj = await self.get(db, id=id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

crud_news = CRUDNews()
