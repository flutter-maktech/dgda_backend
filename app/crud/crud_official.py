from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.official import GovernmentOfficial, ManagementMember
from app.schemas.official import (
    GovernmentOfficialCreate,
    GovernmentOfficialUpdate,
    ManagementMemberCreate,
    ManagementMemberUpdate,
)


class CRUDOfficial:
    # ==========================================
    # 1. GOVERNMENT OFFICIALS (Présidence & Gouv)
    # ==========================================
    async def get_all_government_officials(
        self, db: AsyncSession
    ) -> List[GovernmentOfficial]:
        await self.seed_government_officials_if_empty(db)
        stmt = (
            select(GovernmentOfficial)
            .order_by(GovernmentOfficial.display_order.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_government_official_by_id(
        self, db: AsyncSession, official_id: str
    ) -> Optional[GovernmentOfficial]:
        stmt = select(GovernmentOfficial).where(GovernmentOfficial.id == official_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_government_official(
        self, db: AsyncSession, obj_in: GovernmentOfficialCreate
    ) -> GovernmentOfficial:
        db_obj = GovernmentOfficial(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_government_official(
        self, db: AsyncSession, db_obj: GovernmentOfficial, obj_in: GovernmentOfficialUpdate
    ) -> GovernmentOfficial:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_government_official(
        self, db: AsyncSession, official_id: str
    ) -> bool:
        db_obj = await self.get_government_official_by_id(db, official_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    # ==========================================
    # 2. MANAGEMENT MEMBERS (Direction DGDA)
    # ==========================================
    async def get_all_management_members(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        filter_tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ManagementMember]:
        await self.seed_management_members_if_empty(db)
        stmt = select(ManagementMember).order_by(ManagementMember.display_order.asc())

        if category:
            stmt = stmt.where(ManagementMember.category == category)
        if filter_tag and filter_tag.lower() != "all" and filter_tag.lower() != "tous":
            stmt = stmt.where(ManagementMember.filter_tag == filter_tag)
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                ManagementMember.full_name.ilike(pattern)
                | ManagementMember.role_or_title.ilike(pattern)
                | ManagementMember.department.ilike(pattern)
                | ManagementMember.location.ilike(pattern)
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_management_member_by_id(
        self, db: AsyncSession, member_id: str
    ) -> Optional[ManagementMember]:
        stmt = select(ManagementMember).where(ManagementMember.id == member_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create_management_member(
        self, db: AsyncSession, obj_in: ManagementMemberCreate
    ) -> ManagementMember:
        db_obj = ManagementMember(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_management_member(
        self, db: AsyncSession, db_obj: ManagementMember, obj_in: ManagementMemberUpdate
    ) -> ManagementMember:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_management_member(
        self, db: AsyncSession, member_id: str
    ) -> bool:
        db_obj = await self.get_management_member_by_id(db, member_id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True

    # ==========================================
    # 3. AUTO-SEEDING ROUTINES
    # ==========================================
    async def seed_government_officials_if_empty(self, db: AsyncSession) -> None:
        stmt = select(GovernmentOfficial).limit(1)
        res = await db.execute(stmt)
        if res.scalars().first() is not None:
            return

        initial_officials = [
            GovernmentOfficial(
                id="president_felix_tshisekedi",
                badge_text="PRÉSIDENCE",
                role_title="Président de la République",
                honorific="Son Excellence",
                name="Félix Antoine Tshisekedi Tshilombo",
                photo_path="assets/images/presidence/president_felix_tshisekedi.png",
                mandate_period="2024 - Présent (Second Mandat)",
                cabinet_office="Palais de la Nation, Kinshasa / Gombe",
                official_website="https://presidence.cd",
                display_order=1,
                biography=(
                    "Félix Antoine Tshisekedi Tshilombo est le Président de la République Démocratique du Congo "
                    "depuis janvier 2019, réélu en décembre 2023. En tant que Chef de l'État, il veille au respect de "
                    "la Constitution, assure le fonctionnement régulier des pouvoirs publics et la continuité de l'État."
                ),
                responsibilities=[
                    "Chef de l'État et Commandant suprême des Forces Armées (FARDC)",
                    "Garant de l'indépendance nationale et de l'intégrité territoriale",
                    "Orientation stratégique du développement socio-économique et douanier de la RDC",
                    "Promulgation des lois et représentation de la nation auprès des instances internationales",
                ],
            ),
            GovernmentOfficial(
                id="pm_judith_suminwa",
                badge_text="GOUVERNEMENT",
                role_title="Première Ministre",
                honorific="Son Excellence",
                name="Judith Suminwa Tuluka",
                photo_path="assets/images/presidence/pm_judith_suminwa.png",
                mandate_period="2024 - Présent",
                cabinet_office="Hôtel du Gouvernement, Boulevard du 30 Juin, Kinshasa",
                official_website="https://primature.cd",
                display_order=2,
                biography=(
                    "Judith Suminwa Tuluka est Première Ministre et Chef du Gouvernement de la République Démocratique du Congo, "
                    "première femme à occuper cette haute fonction dans l'histoire du pays. Économiste chevronnée, elle conduit "
                    "la politique de la Nation impulsée par le Président de la République."
                ),
                responsibilities=[
                    "Direction et coordination de l'action gouvernementale",
                    "Exécution des lois et mise en œuvre du programme de développement national",
                    "Supervision des réformes administratives, des recettes publiques et des régies financières",
                    "Engagement pour la création d'emplois et le pouvoir d'achat des ménages",
                ],
            ),
            GovernmentOfficial(
                id="minister_doudou_fwamba",
                badge_text="GOUVERNEMENT",
                role_title="Ministre des Finances",
                honorific="Son Excellence",
                name="Doudou Fwamba Likunde Li-Botayi",
                photo_path="assets/images/presidence/minister_doudou_fwamba.png",
                mandate_period="2024 - Présent",
                cabinet_office="Ministère des Finances, Boulevard du 30 Juin, Kinshasa",
                official_website="https://finances.gouv.cd",
                display_order=3,
                biography=(
                    "Doudou Fwamba Likunde Li-Botayi est Ministre des Finances de la République Démocratique du Congo. "
                    "Cadre supérieur des finances publiques et expert en gestion budgétaire, il exerce la tutelle directe "
                    "sur les régies financières de la République dont la DGDA."
                ),
                responsibilities=[
                    "Tutelle administrative et financière de la DGDA et des régies de recettes",
                    "Pilotage de la politique budgétaire, fiscale et douanière de l'État",
                    "Modernisation et numérisation des procédures de collecte des taxes et accises",
                    "Relations avec les institutions financières internationales (FMI, Banque Mondiale)",
                ],
            ),
        ]

        for off in initial_officials:
            db.add(off)
        await db.commit()

    async def seed_management_members_if_empty(self, db: AsyncSession) -> None:
        stmt = select(ManagementMember).limit(1)
        res = await db.execute(stmt)
        if res.scalars().first() is not None:
            return

        initial_members = [
            # 1. Direction Générale
            ManagementMember(
                id="dg-1",
                full_name="Bernard KABESE MUSANGU",
                role_or_title="DIRECTEUR GÉNÉRAL",
                subtitle="Directeur Général des Douanes et Accises de la RDC",
                department="Direction Générale",
                location="Kinshasa (Siège Social)",
                quote="“Tous mobilisés pour une douane d'action, d'intégrité et d'excellence au service de la Nation.”",
                asset_path="assets/images/management/dg_bernard_kabese_musangu.jpg",
                source_reference="general-01 | Agenda Officiel DGDA 2026, p. 13",
                official_email="direction.generale@douane.gouv.cd",
                official_phone="+243 82 192 0215",
                official_source_url="https://douane.gouv.cd/dgda/structure-organisationnelle/",
                category="directionGenerale",
                is_dg=True,
                display_order=1,
            ),
            ManagementMember(
                id="dga-1",
                full_name="Jean-Louis BAUNA MABOLIA",
                role_or_title="DIRECTEUR GÉNÉRAL ADJOINT",
                subtitle="Directeur Général Adjoint chargé des questions techniques",
                department="Questions Techniques et Opérations Douanières",
                location="Kinshasa (Siège Social)",
                quote="“Optimisation continue des procédures et facilitation sécurisée du commerce extérieur.”",
                asset_path="assets/images/management/dga_jean_louis_bauna.jpg",
                source_reference="general-02 | Agenda Officiel DGDA 2026, p. 13",
                official_email="dga.technique@douane.gouv.cd",
                official_phone="+243 82 192 0215",
                official_source_url="https://douane.gouv.cd/dgda/structure-organisationnelle/",
                category="directionGenerale",
                is_dga=True,
                display_order=2,
            ),
            ManagementMember(
                id="dga-2",
                full_name="Jean-Claude KALENGA MAKONGA",
                role_or_title="DIRECTEUR GÉNÉRAL ADJOINT",
                subtitle="Directeur Général Adjoint chargé des finances et administration",
                department="Finances et Administration Générale",
                location="Kinshasa (Siège Social)",
                quote="“Gouvernance financière rigoureuse, modernisation administrative et valorisation du capital humain.”",
                asset_path="assets/images/management/dga_jean_claude_kalenga.jpg",
                source_reference="general-03 | Agenda Officiel DGDA 2026, p. 13",
                official_email="dga.finances@douane.gouv.cd",
                official_phone="+243 82 192 0215",
                official_source_url="https://douane.gouv.cd/dgda/structure-organisationnelle/",
                category="directionGenerale",
                is_dga=True,
                display_order=3,
            ),
            # 2. Directeurs Centraux (Sélection représentative)
            ManagementMember(
                id="dc-01",
                full_name="Marylou OTSHUMBA OLENGA",
                role_or_title="Bureau de Coordination",
                department="Bureau de Coordination",
                location="Kinshasa (Siège Central)",
                asset_path="assets/images/management/central_01_marylou_otshumba.jpg",
                source_reference="central-01 | Agenda Officiel DGDA, p. 15",
                category="directeursCentraux",
                filter_tag="Bureau",
                display_order=10,
            ),
            ManagementMember(
                id="dc-02",
                full_name="BANGWELA BOGENDA",
                role_or_title="Audit Interne",
                department="Direction de l'Audit Interne",
                location="Kinshasa (Siège Central)",
                asset_path="assets/images/management/central_02_bangwela_bogenda.jpg",
                source_reference="central-02 | Agenda Officiel DGDA, p. 15",
                category="directeursCentraux",
                filter_tag="Direction",
                display_order=11,
            ),
            ManagementMember(
                id="dc-06",
                full_name="David KALANDE MUHIYA",
                role_or_title="Réglementation et Facilitation",
                department="Direction de la Réglementation et Facilitation",
                location="Kinshasa (Siège Central)",
                asset_path="assets/images/management/central_06_david_kalande.jpg",
                source_reference="central-06 | Agenda Officiel DGDA, p. 15",
                category="directeursCentraux",
                filter_tag="Direction",
                display_order=12,
            ),
            # 3. Directeurs Provinciaux
            ManagementMember(
                id="dp-01",
                full_name="Michel BIAYI MUKENDI",
                role_or_title="Directeur Provincial",
                subtitle="Direction Provinciale de Kinshasa-Aéro",
                department="Direction Provinciale Kinshasa-Aéro",
                location="Kinshasa / N'djili",
                asset_path="assets/images/management/dp_kinshasa_aero.jpg",
                source_reference="prov-01 | Agenda Officiel DGDA, p. 22",
                category="directeursProvinciaux",
                filter_tag="Kinshasa",
                display_order=20,
            ),
            ManagementMember(
                id="dp-02",
                full_name="Félicien MWABILU KABWE",
                role_or_title="Directeur Provincial",
                subtitle="Direction Provinciale du Kongo Central",
                department="Direction Provinciale Kongo Central",
                location="Matadi / Boma",
                asset_path="assets/images/management/dp_kongo_central.jpg",
                source_reference="prov-02 | Agenda Officiel DGDA, p. 22",
                category="directeursProvinciaux",
                filter_tag="Kongo Central",
                display_order=21,
            ),
            ManagementMember(
                id="dp-03",
                full_name="Augustin BANZA NGOY",
                role_or_title="Directeur Provincial",
                subtitle="Direction Provinciale du Haut-Katanga",
                department="Direction Provinciale Haut-Katanga",
                location="Lubumbashi / Kasumbalesa",
                asset_path="assets/images/management/dp_katanga.jpg",
                source_reference="prov-03 | Agenda Officiel DGDA, p. 23",
                category="directeursProvinciaux",
                filter_tag="Haut-Katanga",
                display_order=22,
            ),
            # 4. Représentants à l'étranger
            ManagementMember(
                id="re-01",
                full_name="Dieudonné KASONGO MUKALAY",
                role_or_title="Délégué Général Douanes",
                subtitle="Représentation DGDA près l'Union Européenne & OMD",
                department="Représentation Bruxelles",
                location="Bruxelles (Belgique)",
                asset_path="assets/images/management/rep_bruxelles.jpg",
                source_reference="foreign-01 | Agenda Officiel DGDA, p. 28",
                category="representantsEtranger",
                filter_tag="Europe",
                display_order=30,
            ),
            ManagementMember(
                id="re-02",
                full_name="Albert TSHILOMBO KANKU",
                role_or_title="Représentant Portuaire",
                subtitle="Corridor Maritime Est — Port de Mombasa",
                department="Représentation Kenya / Corridor Nord",
                location="Mombasa (Kenya)",
                asset_path="assets/images/management/rep_mombasa.jpg",
                source_reference="foreign-02 | Agenda Officiel DGDA, p. 28",
                category="representantsEtranger",
                filter_tag="Afrique de l'Est",
                display_order=31,
            ),
            # 5. Délégation Syndicale
            ManagementMember(
                id="ds-01",
                full_name="Jean-Marie ILUNGA MBAYO",
                role_or_title="Président National",
                subtitle="Délégation Syndicale Nationale de la DGDA",
                department="Délégation Syndicale Nationale",
                location="Kinshasa (Siège Social)",
                asset_path="assets/images/management/syndicat_president.jpg",
                source_reference="syndicat-01 | Agenda Officiel DGDA, p. 30",
                category="delegationSyndicale",
                filter_tag="Syndicat",
                display_order=40,
            ),
        ]

        for mem in initial_members:
            db.add(mem)
        await db.commit()


crud_official = CRUDOfficial()
