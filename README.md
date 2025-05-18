# My_Agenda_Tkinter
Gestionnaire d’emploi du temps en Python avec interface Tkinter. Permet à un étudiant de planifier ses cours et événements, recevoir des notifications, et visualiser son agenda par jour, semaine ou mois. Le projet utilise une base SQLite, des modèles métier avec dataclasses, et une architecture modulaire.

# 📅 Gestionnaire d’Emploi du Temps – Python & Tkinter

Ce projet est une application de gestion d’emploi du temps personnelle conçue pour les étudiants.  
Développée en Python avec Tkinter, elle permet d’organiser des événements (cours, examens, etc.), de les visualiser par jour/semaine/mois, et de recevoir des notifications.

---

## 🚀 Fonctionnalités

- Authentification par compte étudiant (inscription + connexion)
- Ajout, modification et suppression d’événements
- Vue calendrier : jour, semaine, mois
- Détection automatique des conflits d’horaire
- Notifications de rappel programmées
- Interface graphique simple et ergonomique

---

## 🖼️ Captures d’écran

| Connexion | Vue Semaine | Ajout d'événement | Notification |
|----------|--------------|-------------------|--------------|
| ![](screenshots/connexion.png) | ![](screenshots/vue_semaine.png) | ![](screenshots/ajout.png) | ![](screenshots/notification.png) |

---

## ⚙️ Installation

### Prérequis :
- Python 3.7+
- pip (gestionnaire de paquets)

### Installation :
```bash
git clone https://github.com/ton-pseudo/My_Agenda_Tkinter.git
cd My_Agenda_Tkinter
pip install -r requirements.txt
python main.py
```
⚠️ Le fichier .db est généré automatiquement au premier lancement.


## 🧪 Tests conseillés :
✔️ Connexion/inscription avec un email valide

✔️ Ajout d’un événement sans conflit

✔️ Tentative d’ajout avec chevauchement

✔️ Réception de notification automatique

✔️ Navigation entre les vues

## 🛠️ Technologies utilisées
Python 3

Tkinter (GUI)

SQLite (base de données embarquée)

Pillow (affichage images)

## 📜 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d’informations.

## 🤝 Contribution
Les contributions sont les bienvenues !
Tu peux :

Cloner le dépôt

Créer une branche

Proposer une pull request ✨

## 👨‍💻 Auteur
Maïzan Boni Kobenan Jean Dominique – Étudiant en Sciences et Technologies de l'Information et de la Communication

Projet réalisé dans le cadre de Projet Informatique Encadré
