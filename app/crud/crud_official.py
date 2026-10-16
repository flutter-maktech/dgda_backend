from typing import List, Optional
from sqlalchemy import select, text, func
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
            try:
                await db.execute(
                    text(
                        "UPDATE government_officials SET "
                        "photo_url = '/public/images/officials/' || id || '.png' "
                        "WHERE photo_url IS NULL OR photo_url = ''"
                    )
                )
                await db.commit()
            except Exception:
                await db.rollback()
            return

        initial_officials = [
            GovernmentOfficial(
                id="president_felix_tshisekedi",
                badge_text="PRÉSIDENCE",
                role_title="Président de la République",
                honorific="Son Excellence",
                name="Félix Antoine Tshisekedi Tshilombo",
                photo_path="",
                photo_url="/public/images/officials/president_felix_tshisekedi.png",
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
                photo_path="",
                photo_url="/public/images/officials/pm_judith_suminwa.png",
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
                photo_path="",
                photo_url="/public/images/officials/minister_doudou_fwamba.png",
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
        count_stmt = select(func.count()).select_from(ManagementMember)
        res = await db.execute(count_stmt)
        total_count = res.scalar() or 0

        if total_count >= 50:
            # Ensure no photo_url is null
            try:
                await db.execute(
                    text(
                        "UPDATE management_members SET "
                        "photo_url = '/public/images/management/' || REPLACE(REPLACE(asset_path, 'assets/images/management/', ''), 'assets/images/', '') "
                        "WHERE (photo_url IS NULL OR photo_url = '') AND asset_path IS NOT NULL"
                    )
                )
                await db.commit()
            except Exception:
                await db.rollback()
            return

        if total_count > 0:
            await db.execute(text("DELETE FROM management_members"))
            await db.commit()

        initial_members = [
            ManagementMember(
                id='dg-1',
                full_name='Bernard KABESE MUSANGU',
                role_or_title='DIRECTEUR GÉNÉRAL',
                subtitle='Directeur Général des Douanes et Accises de la RDC',
                department='Direction Générale',
                location='Kinshasa (Siège Social)',
                quote='“Tous mobilisés pour une douane d\\',
                photo_url='/public/images/management/dg_bernard_kabese_musangu.jpg',
                source_reference='general-01 | Agenda Officiel DGDA 2026, p. 13',
                official_email='direction.generale@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/structure-organisationnelle/',
                category='directionGenerale',
                is_dg=True,
                display_order=2,
            ),
            ManagementMember(
                id='dga-1',
                full_name='Jean-Louis BAUNA MABOLIA',
                role_or_title='DIRECTEUR GÉNÉRAL ADJOINT',
                subtitle='Directeur Général Adjoint chargé des questions techniques',
                department='Questions Techniques et Opérations Douanières',
                location='Kinshasa (Siège Social)',
                quote='“Optimisation continue des procédures et facilitation sécurisée du commerce extérieur.”',
                photo_url='/public/images/management/dga_jean_louis_bauna.jpg',
                source_reference='general-02 | Agenda Officiel DGDA 2026, p. 13',
                official_email='dga.technique@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/structure-organisationnelle/',
                category='directionGenerale',
                is_dga=True,
                display_order=3,
            ),
            ManagementMember(
                id='dga-2',
                full_name='Jean-Claude KALENGA MAKONGA',
                role_or_title='DIRECTEUR GÉNÉRAL ADJOINT',
                subtitle='Directeur Général Adjoint chargé des finances et administration',
                department='Finances et Administration Générale',
                location='Kinshasa (Siège Social)',
                quote='“Gouvernance financière rigoureuse, modernisation administrative et valorisation du capital humain.”',
                photo_url='/public/images/management/dga_jean_claude_kalenga.jpg',
                source_reference='general-03 | Agenda Officiel DGDA 2026, p. 13',
                official_email='dga.finances@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/structure-organisationnelle/',
                category='directionGenerale',
                is_dga=True,
                display_order=4,
            ),
            ManagementMember(
                id='dc-01',
                full_name='Marylou OTSHUMBA OLENGA',
                role_or_title='Bureau de Coordination',
                department='Bureau de Coordination',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_01_marylou_otshumba.jpg',
                source_reference='central-01 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Bureau',
                display_order=5,
            ),
            ManagementMember(
                id='dc-02',
                full_name='BANGWELA BOGENDA',
                role_or_title='Audit Interne',
                department='Direction de l\\',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_02_bangwela_bogenda.jpg',
                source_reference='central-02 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=6,
            ),
            ManagementMember(
                id='dc-03',
                full_name='Anicet BELITO BELIE',
                role_or_title='Coordonnateur Audit Interne',
                department='Coordination Audit Interne',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_03_anicet_belito.jpg',
                source_reference='central-03 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=7,
            ),
            ManagementMember(
                id='dc-04',
                full_name='Jean-Claude BOKINGI EMBEYOLO',
                role_or_title='Autres Produits d’Accises',
                department='Direction des Autres Produits d’Accises',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_04_jean_claude_bokingi.jpg',
                source_reference='central-04 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=8,
            ),
            ManagementMember(
                id='dc-05',
                full_name='Guy ESSONGOLA TOLE ESSO',
                role_or_title='Audit Interne',
                department='Direction de l\\',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_05_guy_essongola.jpg',
                source_reference='central-05 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=9,
            ),
            ManagementMember(
                id='dc-06',
                full_name='David KALANDE MUHIYA',
                role_or_title='Réglementation et Facilitation',
                department='Direction de la Réglementation et Facilitation',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_06_david_kalande.jpg',
                source_reference='central-06 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=10,
            ),
            ManagementMember(
                id='dc-07',
                full_name='Symphorien KASINDI YIMBA',
                role_or_title='Audit Interne',
                department='Direction de l\\',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_07_symphorien_kasindi.jpg',
                source_reference='central-07 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=11,
            ),
            ManagementMember(
                id='dc-08',
                full_name='Robert KILEMUNA KUNDA',
                role_or_title='Audit Interne',
                department='Direction de l\\',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_08_robert_kilemuna.jpg',
                source_reference='central-08 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=12,
            ),
            ManagementMember(
                id='dc-09',
                full_name='Réné KISALA MWANIA',
                role_or_title='Huiles Minérales',
                department='Direction des Huiles Minérales',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_09_rene_kisala.jpg',
                source_reference='central-09 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=13,
            ),
            ManagementMember(
                id='dc-10',
                full_name='Richard LEHANI RASHIDI',
                role_or_title='Audit Interne',
                department='Direction de l\\',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_10_richard_lehani.jpg',
                source_reference='central-10 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=14,
            ),
            ManagementMember(
                id='dc-11',
                full_name='Roger LIONDJO LOBOTA',
                role_or_title='Recettes du Trésor',
                department='Direction des Recettes du Trésor',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_11_roger_liondjo.jpg',
                source_reference='central-11 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=15,
            ),
            ManagementMember(
                id='dc-12',
                full_name='Carol LUTALADIO MBUTA',
                role_or_title='Statistiques, Doc. et Etudes Economiques',
                department='Direction des Statistiques et Etudes',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_12_carol_lutaladio.jpg',
                source_reference='central-12 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=16,
            ),
            ManagementMember(
                id='dc-13',
                full_name='Voltaire MAMPINDA ONDJUO',
                role_or_title='Réformes et Modernisation',
                department='Direction des Réformes et Modernisation',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_13_voltaire_mampinda.jpg',
                source_reference='central-13 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=17,
            ),
            ManagementMember(
                id='dc-14',
                full_name='Pierette MBOMBO MUKADI',
                role_or_title='Brigade et Lutte contre la Fraude',
                department='Direction de la Brigade et Lutte contre la Fraude',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_14_pierette_mbombo.jpg',
                source_reference='central-14 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=18,
            ),
            ManagementMember(
                id='dc-15',
                full_name='Jean-Dénis MBOMY MALUKU',
                role_or_title='Tarif et Règles d’Origine',
                department='Direction du Tarif et Règles d’Origine',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_15_jean_denis_mbomy.jpg',
                source_reference='central-15 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=19,
            ),
            ManagementMember(
                id='dc-16',
                full_name='Béatrice MBUYAMBA CIYOLE',
                role_or_title='Audit Interne',
                department='Direction de l\\',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_16_beatrice_mbuyamba.jpg',
                source_reference='central-16 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=20,
            ),
            ManagementMember(
                id='dc-17',
                full_name='Trésor-Patrice MBUAKI MANOKA',
                role_or_title='Affaires Juridiques et Contentieuses',
                department='Direction des Affaires Juridiques',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_17_tresor_patrice_mbuaki.jpg',
                source_reference='central-17 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=21,
            ),
            ManagementMember(
                id='dc-18',
                full_name='Bénie-Gertrude MUBENESHA MPEMBA',
                role_or_title='Finances Internes',
                department='Direction des Finances Internes',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_18_benie_gertrude_mubenesha.jpg',
                source_reference='central-18 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=22,
            ),
            ManagementMember(
                id='dc-19',
                full_name='Roger MUHIMA KALAMO',
                role_or_title='Systèmes et Technologies d’Information',
                department='Direction des Systèmes et Technologies d’Information',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_19_roger_muhima.jpg',
                source_reference='central-19 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=23,
            ),
            ManagementMember(
                id='dc-20',
                full_name='Hugues MUKENGE MABI',
                role_or_title='Ressources Humaines',
                department='Direction des Ressources Humaines',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_20_hugues_mukenge.jpg',
                source_reference='central-20 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=24,
            ),
            ManagementMember(
                id='dc-21',
                full_name='Gabriel MWEPU NUMBI',
                role_or_title='Equipements et Logistique',
                department='Direction des Equipements et Logistique',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_21_gabriel_mwepu.jpg',
                source_reference='central-21 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=25,
            ),
            ManagementMember(
                id='dc-22',
                full_name='Jean NGOY KATSHELEWA',
                role_or_title='Valeur',
                department='Direction de la Valeur en Douane',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_22_jean_ngoy.jpg',
                source_reference='central-22 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=26,
            ),
            ManagementMember(
                id='dc-23',
                full_name='Léon NZITA LUTETE',
                role_or_title='Coordonnateur Adjoint Audit Interne',
                department='Coordination Adjointe Audit Interne',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_23_leon_nzita.jpg',
                source_reference='central-23 | Agenda Officiel DGDA, p. 15',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=27,
            ),
            ManagementMember(
                id='dc-24',
                full_name='BIANDO SANGO',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_24_biando_sango.jpg',
                source_reference='central-24 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=28,
            ),
            ManagementMember(
                id='dc-25',
                full_name='ILUTA EKOFO ESANGAOYI',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_25_iluta_ekofo.jpg',
                source_reference='central-25 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=29,
            ),
            ManagementMember(
                id='dc-26',
                full_name='Boni LITITIYO LUSIKU',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_26_boni_lititiyo.jpg',
                source_reference='central-26 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=30,
            ),
            ManagementMember(
                id='dc-27',
                full_name='MBUYI WA TAMBWE',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_27_mbuyi_wa_tambwe.jpg',
                source_reference='central-27 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=31,
            ),
            ManagementMember(
                id='dc-28',
                full_name='MUVOVA BONDO',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_28_muvova_bondo.jpg',
                source_reference='central-28 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=32,
            ),
            ManagementMember(
                id='dc-29',
                full_name='MVUEMVUE WEKUINA',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_29_mvuemvue_wekuina.jpg',
                source_reference='central-29 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=33,
            ),
            ManagementMember(
                id='dc-30',
                full_name='SHWEKA AMIDA',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_30_shweka_amida.jpg',
                source_reference='central-30 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=34,
            ),
            ManagementMember(
                id='dc-31',
                full_name='SWALEHE ENZEWA',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_31_swalehe_enzewa.jpg',
                source_reference='central-31 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=35,
            ),
            ManagementMember(
                id='dc-32',
                full_name='Angèle TSHIELA BIFUILA',
                role_or_title='Directeur',
                department='Direction Centrale',
                location='Kinshasa (Siège Central)',
                photo_url='/public/images/management/central_32_angele_tshiela.jpg',
                source_reference='central-32 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursCentraux',
                filter_tag='Direction',
                display_order=36,
            ),
            ManagementMember(
                id='dp-01',
                full_name='Zoé BOKANYA LOMBOTO',
                role_or_title='Directeur Provincial — Maniema',
                department='Direction Provinciale des Douanes',
                location='Kindu, Province du Maniema',
                photo_url='/public/images/management/provincial_01_zoe_bokanya.jpg',
                source_reference='provincial-01 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=37,
            ),
            ManagementMember(
                id='dp-02',
                full_name='Levy BUANA KITOKO',
                role_or_title='Directeur Provincial — Sud Kivu',
                department='Direction Provinciale des Douanes',
                location='Bukavu, Province du Sud-Kivu',
                photo_url='/public/images/management/provincial_02_levy_buana.jpg',
                source_reference='provincial-02 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=38,
            ),
            ManagementMember(
                id='dp-03',
                full_name='Dido ILEMBWA BOSEKOMPANDA',
                role_or_title='Directeur Provincial — Tanganyika',
                department='Direction Provinciale des Douanes',
                location='Kalemie, Province du Tanganyika',
                photo_url='/public/images/management/provincial_03_dido_ilembwa.jpg',
                source_reference='provincial-03 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=39,
            ),
            ManagementMember(
                id='dp-04',
                full_name='Réné KALALA MASIMANGO',
                role_or_title='Directeur Provincial — Kinshasa-Ville',
                department='Direction Provinciale des Douanes',
                location='Kinshasa-Ville',
                photo_url='/public/images/management/provincial_04_rene_kalala.jpg',
                source_reference='provincial-04 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=40,
            ),
            ManagementMember(
                id='dp-05',
                full_name='Paul KAYEMBE NGINDU',
                role_or_title='Directeur Provincial — Nord-Kivu',
                department='Direction Provinciale des Douanes',
                location='Goma, Province du Nord-Kivu',
                photo_url='/public/images/management/provincial_05_paul_kayembe.jpg',
                source_reference='provincial-05 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=41,
            ),
            ManagementMember(
                id='dp-06',
                full_name='Felly KITENGE YAMWILA',
                role_or_title='Directeur Provincial — Ituri',
                department='Direction Provinciale des Douanes',
                location='Bunia, Province de l\\',
                photo_url='/public/images/management/provincial_06_felly_kitenge.jpg',
                source_reference='provincial-06 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=42,
            ),
            ManagementMember(
                id='dp-07',
                full_name='Willy KITIMUNA LWANGA',
                role_or_title='Directeur Provincial — Bandundu',
                department='Direction Provinciale des Douanes',
                location='Bandundu (Kwilu, Kwango, Mai-Ndombe)',
                photo_url='/public/images/management/provincial_07_willy_kitimuna.jpg',
                source_reference='provincial-07 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=43,
            ),
            ManagementMember(
                id='dp-08',
                full_name='Bernard LIKUNDE NGANDI',
                role_or_title='Directeur Provincial — Tshopo, Bas-Uele et Haut-Uele',
                department='Direction Provinciale des Douanes',
                location='Kisangani, Grande Province Orientale',
                photo_url='/public/images/management/provincial_08_bernard_likunde.jpg',
                source_reference='provincial-08 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=44,
            ),
            ManagementMember(
                id='dp-09',
                full_name='Orly MBUTU PHANZU',
                role_or_title='Directeur Provincial — Kasaï Occidental',
                department='Direction Provinciale des Douanes',
                location='Kananga (Kasaï et Kasaï Central)',
                photo_url='/public/images/management/provincial_09_orly_mbutu.jpg',
                source_reference='provincial-09 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=45,
            ),
            ManagementMember(
                id='dp-10',
                full_name='Ildephonse MUBIBYA SILUTALA',
                role_or_title='Directeur Provincial — Kinshasa-Aéro',
                department='Direction Provinciale Aéronautique',
                location='Aéroport International de N\\',
                photo_url='/public/images/management/provincial_10_ildephonse_mubibya.jpg',
                source_reference='provincial-10 | Agenda Officiel DGDA, p. 16',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=46,
            ),
            ManagementMember(
                id='dp-11',
                full_name='Carl MUKULUTU MAYANGA',
                role_or_title='Directeur Provincial — Kasaï Oriental',
                department='Direction Provinciale des Douanes',
                location='Mbuji-Mayi, Province du Kasaï Oriental',
                photo_url='/public/images/management/provincial_11_carl_mukulutu.jpg',
                source_reference='provincial-11 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=47,
            ),
            ManagementMember(
                id='dp-12',
                full_name='Sabine MUSSIMBI BIBI',
                role_or_title='Directeur Provincial — Equateur',
                department='Direction Provinciale des Douanes',
                location='Mbandaka, Province de l\\',
                photo_url='/public/images/management/provincial_12_sabine_mussimbi.jpg',
                source_reference='provincial-12 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=48,
            ),
            ManagementMember(
                id='dp-13',
                full_name='Evariste NTAMBUE KANKU',
                role_or_title='Directeur Provincial — Haut-Katanga',
                department='Direction Provinciale des Douanes',
                location='Lubumbashi (Kasumbalesa, Mokambo)',
                photo_url='/public/images/management/provincial_13_evariste_ntambue.jpg',
                source_reference='provincial-13 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=49,
            ),
            ManagementMember(
                id='dp-14',
                full_name='Narcisse PHAMBU NGEMBO',
                role_or_title='Directeur Provincial — Lualaba et Haut-Lomami',
                department='Direction Provinciale des Douanes',
                location='Kolwezi, Province du Lualaba',
                photo_url='/public/images/management/provincial_14_narcisse_phambu.jpg',
                source_reference='provincial-14 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=50,
            ),
            ManagementMember(
                id='dp-15',
                full_name='Alain TENDAY LUPUMBA',
                role_or_title='Directeur Provincial — Kongo-Central',
                department='Direction Provinciale des Douanes',
                location='Matadi (Ports de Matadi, Boma, Poste de Lufu)',
                photo_url='/public/images/management/provincial_15_alain_tenday.jpg',
                source_reference='provincial-15 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='directeursProvinciaux',
                filter_tag='Province',
                display_order=51,
            ),
            ManagementMember(
                id='re-01',
                full_name='Jean-Pièrre DALE KOYANGALO',
                role_or_title='Représentant Douanier — Kampala',
                department='Représentation Douanière RDC',
                location='Kampala, Ouganda (Corridor Nord)',
                photo_url='/public/images/management/abroad_01_jean_pierre_dale.jpg',
                source_reference='abroad-01 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='representantsEtranger',
                filter_tag='Pays',
                display_order=52,
            ),
            ManagementMember(
                id='re-02',
                full_name='Jean-Paul ESAMBA BOKEL’IPOKA',
                role_or_title='Représentant Douanier — Douala',
                department='Représentation Douanière RDC',
                location='Douala, Cameroun (Afrique Centrale / CEMAC)',
                photo_url='/public/images/management/abroad_02_jean_paul_esamba.jpg',
                source_reference='abroad-02 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='representantsEtranger',
                filter_tag='Représentation',
                display_order=53,
            ),
            ManagementMember(
                id='re-03',
                full_name='John KABANGE MUKUBU',
                role_or_title='Représentant Douanier — Bruxelles',
                department='Représentation Douanière RDC',
                location='Bruxelles, Belgique (Union Européenne / OMD)',
                photo_url='/public/images/management/abroad_03_john_kabange.jpg',
                source_reference='abroad-03 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='representantsEtranger',
                filter_tag='Représentation',
                display_order=54,
            ),
            ManagementMember(
                id='re-04',
                full_name='Freddy LWETE LWENKOMBA',
                role_or_title='Représentant Douanier — Dar-Es-salaam',
                department='Représentation Douanière RDC',
                location='Dar-Es-salaam, Tanzanie (Corridor Central)',
                photo_url='/public/images/management/abroad_04_freddy_lwete.jpg',
                source_reference='abroad-04 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='representantsEtranger',
                filter_tag='Pays',
                display_order=55,
            ),
            ManagementMember(
                id='re-05',
                full_name='Freddy MPATA KALVANDA',
                role_or_title='Représentant Douanier — Mombasa',
                department='Représentation Douanière RDC',
                location='Mombasa, Kenya (Port de Transit Ouest-Indien)',
                photo_url='/public/images/management/abroad_05_freddy_mpata.jpg',
                source_reference='abroad-05 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='representantsEtranger',
                filter_tag='Représentation',
                display_order=56,
            ),
            ManagementMember(
                id='ds-01',
                full_name='Désiré ITEGWA NCHIKO',
                role_or_title='Président',
                subtitle='Président de la Délégation Syndicale Nationale DGDA',
                department='Délégation Syndicale Nationale',
                location='Kinshasa (Direction Générale)',
                photo_url='/public/images/management/union_01_desire_itegwa.jpg',
                source_reference='union-01 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='delegationSyndicale',
                display_order=57,
            ),
            ManagementMember(
                id='ds-02',
                full_name='Marceline MACHOZI ATIBU',
                role_or_title='1ère Vice-Présidente',
                subtitle='1ère Vice-Présidente de la Délégation Syndicale Nationale DGDA',
                department='Délégation Syndicale Nationale',
                location='Kinshasa (Direction Générale)',
                photo_url='/public/images/management/union_02_marceline_machozi.jpg',
                source_reference='union-02 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='delegationSyndicale',
                display_order=58,
            ),
            ManagementMember(
                id='ds-03',
                full_name='Jean-Pierre KABOMBO BADIABIABO',
                role_or_title='2ème Vice-Président',
                subtitle='2ème Vice-Président de la Délégation Syndicale Nationale DGDA',
                department='Délégation Syndicale Nationale',
                location='Kinshasa (Direction Générale)',
                photo_url='/public/images/management/union_03_jean_pierre_kabombo.jpg',
                source_reference='union-03 | Agenda Officiel DGDA, p. 17',
                official_email='contact@douane.gouv.cd',
                official_phone='+243 82 192 0215',
                official_source_url='https://douane.gouv.cd/dgda/services/',
                category='delegationSyndicale',
                display_order=59,
            ),
        ]

        for mem in initial_members:
            db.add(mem)
        await db.commit()


crud_official = CRUDOfficial()
