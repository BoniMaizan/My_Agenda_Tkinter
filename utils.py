from datetime import datetime, timedelta
import threading
import time
from db import obtenir_notifications,obtenir_evenements

def verifier_conflits_horaires(etudiant_id, nouvelle_date_debut, nouvelle_date_fin):
    """Vérifie si le nouvel événement entre en conflit avec des événements existants"""
    # Convertir en objets datetime pour comparaison
    try:
        debut = datetime.strptime(nouvelle_date_debut, "%Y-%m-%d %H:%M")
        fin = datetime.strptime(nouvelle_date_fin, "%Y-%m-%d %H:%M")
    except ValueError:
        return False  # Format invalide
    
    # Récupérer les événements qui se chevauchent
    evenements = obtenir_evenements(
        etudiant_id,
        nouvelle_date_debut,
        nouvelle_date_fin
    )
    
    return len(evenements) > 0

def demarrer_verification_notifications(app_instance):
    """Démarre un thread pour vérifier les notifications périodiquement"""
    def verifier():
        while True:
            if hasattr(app_instance, 'etudiant_connecte') and app_instance.etudiant_connecte:
                notifications = obtenir_notifications(
                    app_instance.etudiant_connecte['Identifiant_Etudiant'],
                    non_lues_seulement=True
                )
                for notif in notifications:
                    app_instance.after(0, app_instance.afficher_notification, notif)
            time.sleep(60)  # Vérifier toutes les minutes
    
    thread = threading.Thread(target=verifier, daemon=True)
    thread.start()

def formater_duree(minutes):
    """Convertit une durée en minutes en format lisible (ex: 2h30)"""
    heures = minutes // 60
    minutes_restantes = minutes % 60
    return f"{heures}h{minutes_restantes:02d}" if heures > 0 else f"{minutes_restantes}min"