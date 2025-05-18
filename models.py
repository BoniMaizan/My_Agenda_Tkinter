from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Etudiant:
    id: int
    nom: str
    mail: str

@dataclass
class Evenement:
    id: int
    nom: str
    date_debut: datetime
    date_fin: datetime
    duree: int  # en minutes
    type_event: str
    couleur: str
    description: str
    etudiant_id: int

@dataclass
class Notification:
    id: int
    message: str
    date_envoi: datetime
    statut: str  # 'Lu' ou 'Non lu'
    evenement_id: Optional[int]
    etudiant_id: int

def dict_to_evenement(data: dict) -> Evenement:
    return Evenement(
        id=data['Identifiant_Evenement'],
        nom=data['nom_evenement'],
        date_debut=datetime.strptime(data['date_heure_debut_Evenement'], "%Y-%m-%d %H:%M"),
        date_fin=datetime.strptime(data['date_heure_fin_Evenement'], "%Y-%m-%d %H:%M"),
        duree=data['duree_Evenement'],
        type_event=data['type_Evenement'],
        couleur=data['couleur_evenement'],
        description=data['description'],
        etudiant_id=data['Identifiant_Etudiant']
    )

def dict_to_notification(data: dict) -> Notification:
    return Notification(
        id=data['Identifiant_Notification'],
        message=data['message_Notification'],
        date_envoi=datetime.strptime(data['date_envoi_Notification'], "%Y-%m-%d %H:%M"),
        statut=data['statut_Notification'],
        evenement_id=data.get('Identifiant_Evenement'),
        etudiant_id=data['Identifiant_Etudiant']
    )