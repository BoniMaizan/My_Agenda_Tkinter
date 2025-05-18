import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('emploi_du_temps.db')
    cursor = conn.cursor()
    
    # Création des tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Etudiant (
        Identifiant_Etudiant INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_Etudiant TEXT NOT NULL,
        mail_Etudiant TEXT NOT NULL UNIQUE,
        mot_de_passe TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Emploi_du_temps (
        Identifiant_Emploi_du_temps INTEGER PRIMARY KEY AUTOINCREMENT,
        Semaine_Emploi_du_temps INTEGER NOT NULL,
        Identifiant_Etudiant INTEGER,
        FOREIGN KEY(Identifiant_Etudiant) REFERENCES Etudiant(Identifiant_Etudiant)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Evenement (
        Identifiant_Evenement INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_evenement TEXT NOT NULL,
        date_heure_debut_Evenement TEXT NOT NULL,
        date_heure_fin_Evenement TEXT NOT NULL,
        duree_Evenement INTEGER NOT NULL,
        type_Evenement TEXT,
        couleur_evenement TEXT,
        description TEXT,
        Identifiant_Etudiant INTEGER,
        FOREIGN KEY(Identifiant_Etudiant) REFERENCES Etudiant(Identifiant_Etudiant)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Notification (
        Identifiant_Notification INTEGER PRIMARY KEY AUTOINCREMENT,
        message_Notification TEXT NOT NULL,
        date_envoi_Notification TEXT NOT NULL,
        statut_Notification TEXT NOT NULL,
        Identifiant_Evenement INTEGER,
        Identifiant_Etudiant INTEGER,
        FOREIGN KEY(Identifiant_Etudiant) REFERENCES Etudiant(Identifiant_Etudiant),
        FOREIGN KEY(Identifiant_Evenement) REFERENCES Evenement(Identifiant_Evenement)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('emploi_du_temps.db')
    conn.row_factory = sqlite3.Row
    return conn

def creer_etudiant(nom, mail, mot_de_passe):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Etudiant (nom_Etudiant, mail_Etudiant, mot_de_passe) VALUES (?, ?, ?)",
            (nom, mail, mot_de_passe)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def verifier_connexion(mail, mot_de_passe):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Etudiant WHERE mail_Etudiant = ? AND mot_de_passe = ?",
        (mail, mot_de_passe))
    etudiant = cursor.fetchone()
    conn.close()
    return etudiant

def ajouter_evenement(etudiant_id, nom, date_debut, date_fin, type_event, couleur, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calcul de la durée en minutes
    debut = datetime.strptime(date_debut, "%Y-%m-%d %H:%M")
    fin = datetime.strptime(date_fin, "%Y-%m-%d %H:%M")
    duree = int((fin - debut).total_seconds() / 60)
    
    cursor.execute(
        '''INSERT INTO Evenement (
            nom_evenement, date_heure_debut_Evenement, date_heure_fin_Evenement, 
            duree_Evenement, type_Evenement, couleur_evenement, description, Identifiant_Etudiant
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (nom, date_debut, date_fin, duree, type_event, couleur, description, etudiant_id)
    )
    
    # Créer une notification pour cet événement
    notif_message = f"Rappel: {nom} commence à {date_debut.split(' ')[1]}"
    cursor.execute(
        '''INSERT INTO Notification (
            message_Notification, date_envoi_Notification, 
            statut_Notification, Identifiant_Evenement, Identifiant_Etudiant
        ) VALUES (?, ?, ?, ?, ?)''',
        (notif_message, date_debut, 'Non lu', cursor.lastrowid, etudiant_id)
    )
    
    conn.commit()
    conn.close()

def obtenir_evenements(etudiant_id, date_debut=None, date_fin=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if date_debut and date_fin:
        cursor.execute(
            '''SELECT * FROM Evenement 
            WHERE Identifiant_Etudiant = ? 
            AND date_heure_debut_Evenement BETWEEN ? AND ?
            ORDER BY date_heure_debut_Evenement''',
            (etudiant_id, date_debut, date_fin)
        )
    else:
        cursor.execute(
            '''SELECT * FROM Evenement 
            WHERE Identifiant_Etudiant = ? 
            ORDER BY date_heure_debut_Evenement''',
            (etudiant_id,)
        )
    
    evenements = cursor.fetchall()
    conn.close()
    return evenements

def supprimer_evenement(evenement_id, etudiant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Supprimer les notifications associées
    cursor.execute(
        "DELETE FROM Notification WHERE Identifiant_Evenement = ? AND Identifiant_Etudiant = ?",
        (evenement_id, etudiant_id)
    )
    
    # Supprimer l'événement
    cursor.execute(
        "DELETE FROM Evenement WHERE Identifiant_Evenement = ? AND Identifiant_Etudiant = ?",
        (evenement_id, etudiant_id)
    )
    
    conn.commit()
    conn.close()

def obtenir_notifications(etudiant_id, non_lues_seulement=True):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if non_lues_seulement:
        cursor.execute(
            '''SELECT n.*, e.nom_evenement 
            FROM Notification n
            JOIN Evenement e ON n.Identifiant_Evenement = e.Identifiant_Evenement
            WHERE n.Identifiant_Etudiant = ? AND n.statut_Notification = 'Non lu'
            ORDER BY n.date_envoi_Notification''',
            (etudiant_id,)
        )
    else:
        cursor.execute(
            '''SELECT n.*, e.nom_evenement 
            FROM Notification n
            JOIN Evenement e ON n.Identifiant_Evenement = e.Identifiant_Evenement
            WHERE n.Identifiant_Etudiant = ?
            ORDER BY n.date_envoi_Notification''',
            (etudiant_id,)
        )
    
    notifications = cursor.fetchall()
    conn.close()
    return notifications

def marquer_notification_comme_lue(notification_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Notification SET statut_Notification = 'Lu' WHERE Identifiant_Notification = ?",
        (notification_id,)
    )
    conn.commit()
    conn.close()