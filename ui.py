import tkinter as tk
from PIL import Image, ImageTk
from tkinter import LEFT, ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from db import *
from models import dict_to_evenement
import calendar
import threading
import time


class Style:
    COLORS = {
        'background': 'white',
        'sidebar': '#f0f0f0',
        'card': '#ffffff',
        'text': '#333333',
        'primary': '#3d5afe',
        'secondary': '#6200ea',
        'danger': '#ff1744'
    }
    
    @staticmethod
    def configure_button(button, color='primary'):
        button.config(
            bg=Style.COLORS[color],
            fg='white',
            borderwidth=0,
            padx=12,
            pady=6,
            font=('codec pro extrabold', 10),
            activebackground=Style.COLORS[color],
            activeforeground='white'
        )

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="Entrez du texte...", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, e):
        if self['fg'] == self.placeholder_color:
            self.delete(0, 'end')
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MY AGENDA")
        self.geometry("1200x800")
        self.minsize(1010, 600)
        self.configure(bg=Style.COLORS['background']) 
        self.state('zoomed')
        icon = tk.PhotoImage(file="EmploiduTemps/Assets/AppIcon.png")
        self.iconphoto(True, icon)

        # Variables d'état
        self.etudiant_connecte = None
        self.current_view = 'week'  # 'day', 'week', 'month'
        self.current_date = datetime.now()
        
        # Initialiser la base de données
        init_db()
        
        # Afficher l'écran de connexion
        self.afficher_ecran_connexion()
        
        # Démarrer le thread de vérification des notifications
        self.demarrer_verification_notifications()
    
    def demarrer_verification_notifications(self):
        def verifier_notifications():
            while True:
                if self.etudiant_connecte:
                    notifications = obtenir_notifications(self.etudiant_connecte['Identifiant_Etudiant'])
                    for notif in notifications:
                        if notif['statut_Notification'] == 'Non lu':
                            self.after(0, self.afficher_notification, notif)
                time.sleep(60)  # Vérifier toutes les minutes
        
        thread = threading.Thread(target=verifier_notifications, daemon=True)
        thread.start()
    
    def afficher_notification(self, notification):
        # Créer une fenêtre popup de notification
        popup = tk.Toplevel(self)
        popup.title("Notification")
        popup.geometry("300x150")
        
        message = f"{notification['nom_evenement']}\n{notification['message_Notification']}"
        tk.Label(popup, text=message, padx=20, pady=20).pack()
        
        tk.Button(
            popup, 
            text="OK", 
            command=lambda: [marquer_notification_comme_lue(notification['Identifiant_Notification']), popup.destroy()]
        ).pack(pady=10)
        
        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)
    
    def afficher_ecran_connexion(self):
        self.effacer_interface()
        # Open the image and resize its
        original_img = Image.open("EmploiduTemps/Assets/SIGNIN.png")
        resized_img = original_img.resize((558, 417))  # Resize to desired dimensions
        self.background_log = ImageTk.PhotoImage(resized_img)  # Store as an attribute
        tk.Label(self, image=self.background_log, bg='white').place(relx=0.0, rely=0.5, anchor='w')  # Place the image at the extreme left

        # Create a frame for the login form
        frame = tk.Frame(self, width=350, height=350, bg="white")
        frame.place(relx=0.7, rely=0.2, anchor='n')  # Adjust position

        # Heading
        heading = tk.Label(frame, text='CONNEXION', fg='#57a1f8', bg='white', font=('Codec pro extrabold', 23, 'bold'))
        heading.pack(pady=10)

        # Email entry
        self.entry_mail = EntryWithPlaceholder(frame, placeholder="Adresse mail", color='grey', width=25, fg='black', border=0, bg="white", font=('Codec pro extrabold', 11))
        self.entry_mail.pack(pady=10, padx=20, anchor='e')
        tk.Frame(frame, width=295, height=2, bg='black').pack(pady=5)

        # Password entry
        self.entry_mdp = EntryWithPlaceholder(frame, placeholder="Mot de passe", color='grey', width=25, fg='black', border=0, bg="white", font=('Codec pro extrabold', 11))
        self.entry_mdp.bind("<KeyRelease>", lambda e: self.entry_mdp.config(show="*" if self.entry_mdp.get() else ""))
        self.entry_mdp.pack(pady=10, padx=20, anchor='e')
        tk.Frame(frame, width=295, height=2, bg='black').pack(pady=5)

        # Frame for buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.place(relx=0.7, rely=0.8, anchor='n')  # Adjust position

        # Already registered label
        tk.Label(button_frame, text="Pas encore inscrit ?", fg='black', bg='white', font=('Codec pro extrabold', 9)).pack(pady=5)

        # Register button
        tk.Button(
            button_frame, 
            width=18, 
            pady=7, 
            text="S'inscrire", 
            bg='white', 
            fg='#57a1f8', 
            border=1, 
            font=('Codec pro extrabold', 11), 
            command=self.afficher_ecran_inscription
        ).pack(side=LEFT, padx=10)

        # Login button
        tk.Button(
            button_frame, 
            width=18, 
            pady=7, 
            text="Se connecter", 
            bg='#57a1f8', 
            fg='white', 
            border=0, 
            font=('Codec pro extrabold', 11), 
            command=self.connexion
        ).pack(side=LEFT, padx=10)

    def afficher_ecran_inscription(self):
        self.effacer_interface()

    
        # Cree une frame pour le texte de bienvenue en dessous de l'image avec une dimension de 350x350
        welcome_frame = tk.Frame(self, bg='white', width=100, height=10)
        welcome_frame.place(relx=0.0, rely=1.0, anchor='sw')  # Place en bas à gauche sous l'image
        tk.Label(
            welcome_frame,
            text="Bienvenue,\ncette application a été conçue pour \nvous aider à planifier votre planning",
            fg='#57a1f8',
            bg='white',
            font=('Codec pro extrabold', 12, 'bold'),
            anchor="ne",
            justify="center"
        ).pack(padx=170, pady=65)

        # Open the image and resize its
        original_img = Image.open("EmploiduTemps/Assets/LOGIN.png")
        resized_img = original_img.resize((592, 395))  # Resize to desired dimensions
        self.background_log = ImageTk.PhotoImage(resized_img)  # Store as an attribute
        tk.Label(self, image=self.background_log, bg='white').place(relx=0.0, rely=0.5, anchor='w')  # Place the image at the extreme left

        # Create a frame for the login form
        frame = tk.Frame(self, width=350, height=350, bg="white")
        frame.place(relx=0.7, rely=0.2, anchor='n')  # Adjust position

        # Heading
        heading = tk.Label(frame, text='INSCRIPTION', fg='#57a1f8', bg='white', font=('Codec pro extrabold', 23, 'bold'))
        heading.pack(pady=10)

        # Full name entry
        self.entry_name = EntryWithPlaceholder(frame, placeholder="Noms et prénoms", color='grey', width=25, fg='black', border=0, bg="white", font=('Codec pro extrabold', 11))
        self.entry_name.pack(pady=10, padx=20, anchor='e')
        tk.Frame(frame, width=295, height=2, bg='black').pack(pady=5)

        # Email entry
        self.entry_mail = EntryWithPlaceholder(frame, placeholder="Adresse mail", color='grey', width=25, fg='black', border=0, bg="white", font=('Codec pro extrabold', 11))
        self.entry_mail.pack(pady=10, padx=20, anchor='e')
        tk.Frame(frame, width=295, height=2, bg='black').pack(pady=5)

        # Password entry
        self.entry_mdp = EntryWithPlaceholder(frame, placeholder="Mot de passe", color='grey', width=25, fg='black', border=0, bg="white", font=('Codec pro extrabold', 11))
        self.entry_mdp.bind("<KeyRelease>", lambda e: self.entry_mdp.config(show="*" if self.entry_mdp.get() else ""))
        self.entry_mdp.pack(pady=10, padx=20, anchor='e')
        tk.Frame(frame, width=295, height=2, bg='black').pack(pady=5)

       # Frame for buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.place(relx=0.7, rely=0.8, anchor='s')  # Adjust position

        # Already registered label
        tk.Label(frame, text="Déjà inscrit ?", fg='black', bg='white', font=('Codec pro extrabold', 9)).pack(pady=5)

        # Register button
        tk.Button(
            button_frame, 
            width=18, 
            pady=7, 
            text="Se connecter", 
            bg='white', 
            fg='#57a1f8', 
            border=1, 
            font=('Codec pro extrabold', 11), 
            command=self.afficher_ecran_connexion
        ).pack(side=LEFT, padx=10)

        # Login button
        tk.Button(
            button_frame, 
            width=18, 
            pady=7, 
            text="S'inscrire", 
            bg='#57a1f8', 
            fg='white', 
            border=0, 
            font=('Codec pro extrabold', 11), 
            command=self.inscription    
        ).pack(side=LEFT, padx=10)

    def connexion(self):
        mail = self.entry_mail.get()
        mdp = self.entry_mdp.get()
        
        if not mail or not mdp:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        etudiant = verifier_connexion(mail, mdp)
        if etudiant:
            self.etudiant_connecte = etudiant
            self.afficher_interface_principale()
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect")
    
    def inscription(self):
        nom = self.entry_name.get()
        mail = self.entry_mail.get()
        mdp = self.entry_mdp.get()
        
        if not nom or not mail or not mdp:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        etudiant_id = creer_etudiant(nom, mail, mdp)
        if etudiant_id:
            messagebox.showinfo("Succès", "Inscription réussie!")
            self.connexion()
        else:
            messagebox.showerror("Erreur", "Cet email est déjà utilisé")
    
    def afficher_interface_principale(self):
        self.effacer_interface()
        
        # Configuration de la fenêtre principale
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Sidebar (à gauche)
        sidebar = tk.Frame(self, bg=Style.COLORS['sidebar'], width=200)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        
        # Logo / Titre
        tk.Label(
            sidebar, 
            text="Emploi du Temps", 
            font=('codec pro extrabold', 14, 'bold'), 
            bg=Style.COLORS['sidebar'], 
            fg=Style.COLORS['primary'],
            padx=20,
            pady=20
        ).pack()
        
        # Menu
        menu_items = [
            ("Aujourd'hui", self.afficher_aujourdhui),
            ("Jour", lambda: self.changer_vue('day')),
            ("Semaine", lambda: self.changer_vue('week')),
            ("Mois", lambda: self.changer_vue('month')),
            ("Déconnexion", self.deconnexion)
        ]
        
        for text, command in menu_items:
            btn = tk.Button(
                sidebar, 
                text=text, 
                command=command,
                anchor='w',
                padx=20,
                pady=10,
                borderwidth=0,
                font=('codec pro extrabold', 10),
                bg=Style.COLORS['sidebar'],
                fg=Style.COLORS['text'],
                activebackground=Style.COLORS['sidebar'],
                activeforeground=Style.COLORS['primary']
            )
            btn.pack(fill='x')
        
        # En-tête (en haut)
        header = tk.Frame(self, bg=Style.COLORS['background'], height=60)
        header.grid(row=0, column=1, sticky="ew")
        
        # Boutons de navigation
        nav_frame = tk.Frame(header, bg=Style.COLORS['background'])
        nav_frame.pack(side='left', padx=20)
        
        btn_prev = tk.Button(
            nav_frame, 
            text="<", 
            command=self.previous_period,
            font=('codec pro extrabold', 12),
            width=3,
            borderwidth=0,
            bg=Style.COLORS['background'],
            fg=Style.COLORS['text']
        )
        btn_prev.pack(side='left')
        
        self.label_periode = tk.Label(
            nav_frame, 
            text="", 
            font=('codec pro extrabold', 12),
            bg=Style.COLORS['background'],
            fg=Style.COLORS['text']
        )
        self.label_periode.pack(side='left', padx=10)
        
        btn_next = tk.Button(
            nav_frame, 
            text=">", 
            command=self.next_period,
            font=('codec pro extrabold', 12),
            width=3,
            borderwidth=0,
            bg=Style.COLORS['background'],
            fg=Style.COLORS['text']
        )
        btn_next.pack(side='left')
        
        # Bouton ajouter événement
        btn_add = tk.Button(
            header, 
            text="+ Ajouter", 
            command=self.ajouter_evenement_popup_v2,
            bg=Style.COLORS['primary'],
            fg='white',
            font=('codec pro extrabold', 10),
            padx=12,
            pady=6,
            borderwidth=0
        )
        btn_add.pack(side='right', padx=20)
        
        # Contenu principal
        self.main_content = tk.Frame(self, bg=Style.COLORS['background'])
        self.main_content.grid(row=1, column=1, sticky="nsew")
        
        # Afficher la vue par défaut
        self.changer_vue(self.current_view)
    
    def changer_vue(self, vue):
        self.current_view = vue
        self.afficher_vue()
    
    def afficher_vue(self):
        # Effacer le contenu précédent
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Mettre à jour le label de période
        if self.current_view == 'week':
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            self.label_periode.config(text=f"{start_of_week.strftime('%d %b %Y')} - {end_of_week.strftime('%d %b %Y')}")
        elif self.current_view == 'month':
            self.label_periode.config(text=self.current_date.strftime("%B %Y"))
        else:  # day
            self.label_periode.config(text=self.current_date.strftime("%A %d %B %Y"))
        
        # Récupérer les événements pour la période
        if self.current_view == 'week':
            start_date = (self.current_date - timedelta(days=self.current_date.weekday())).strftime("%Y-%m-%d 00:00")
            end_date = (self.current_date + timedelta(days=6 - self.current_date.weekday())).strftime("%Y-%m-%d 23:59")
        elif self.current_view == 'month':
            _, last_day = calendar.monthrange(self.current_date.year, self.current_date.month)
            start_date = self.current_date.replace(day=1).strftime("%Y-%m-%d 00:00")
            end_date = self.current_date.replace(day=last_day).strftime("%Y-%m-%d 23:59")
        else:  # day
            start_date = self.current_date.strftime("%Y-%m-%d 00:00")
            end_date = self.current_date.strftime("%Y-%m-%d 23:59")
        
        evenements = obtenir_evenements(
            self.etudiant_connecte['Identifiant_Etudiant'],
            start_date,
            end_date
        )
        
        # Afficher la vue appropriée
        if self.current_view == 'week':
            self.afficher_vue_semaine(evenements)
        elif self.current_view == 'month':
            self.afficher_vue_mois(evenements)
        else:  # day
            self.afficher_vue_jour(evenements)
    
    def afficher_vue_semaine(self, evenements):
        # Créer un tableau pour la semaine
        tableau = tk.Frame(self.main_content, bg=Style.COLORS['background'])
        tableau.pack(fill='both', expand=True, padx=20, pady=20)
        
        # En-têtes des jours
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        jours = [(start_of_week + timedelta(days=i)) for i in range(7)]
        
        for col, jour in enumerate(jours):
            # En-tête du jour
            header_frame = tk.Frame(
                tableau, 
                bg='white', 
                highlightbackground='#e0e0e0', 
                highlightthickness=1
            )
            header_frame.grid(row=0, column=col, sticky="nsew")
            
            # Nom du jour et date
            jour_label = tk.Label(
                header_frame, 
                text=f"{jour.strftime('%A')[:3]}\n{jour.day}", 
                font=('codec pro extrabold', 10),
                bg='white'
            )
            jour_label.pack(pady=5)
            
            # Événements pour ce jour
            events_frame = tk.Frame(
                tableau, 
                bg='white', 
                highlightbackground='#e0e0e0', 
                highlightthickness=1,

            )
            events_frame.grid(row=1, column=col, sticky="nsew")
            
            # Ajuster la taille des colonnes
            tableau.columnconfigure(col, weight=1)
            
            # Filtrer les événements pour ce jour
            jour_str = jour.strftime("%Y-%m-%d")
            evenements_jour = [
                e for e in evenements 
                if e['date_heure_debut_Evenement'].startswith(jour_str)
            ]
            
            # Afficher les événements
            for event in evenements_jour:
                debut = datetime.strptime(event['date_heure_debut_Evenement'], "%Y-%m-%d %H:%M")
                fin = datetime.strptime(event['date_heure_fin_Evenement'], "%Y-%m-%d %H:%M")
                duree_minutes = int((fin - debut).total_seconds() // 60)
                # Par exemple, 1 minute = 1.5 pixels (à ajuster selon la taille de ta colonne)
                hauteur = max(20, int(duree_minutes * 0.5))

                event_card = tk.Frame(
                    events_frame, 
                    bg=event['couleur_evenement'] or Style.COLORS['primary'],
                    padx=5,
                    pady=2,
                    highlightbackground='#e0e0e0',
                    highlightthickness=1,
                    width=20,
                    height=hauteur
                )
                event_card.pack(fill='x', pady=2)
                event_card.pack_propagate(False)  # Pour forcer la hauteur

                event_text = f"{debut.strftime('%H:%M')}-{fin.strftime('%H:%M')}\n{event['nom_evenement']}"
                tk.Label(
                    event_card, 
                    text=event_text, 
                    font=('codec pro extrabold', 9),
                    bg=event['couleur_evenement'] or Style.COLORS['primary'],
                    fg='white',
                    anchor='w'
                ).pack(fill='x')

                event_card.bind("<Button-1>", lambda _, ev=event: self.afficher_details_evenement(ev))
                for child in event_card.winfo_children():
                    child.bind("<Button-1>", lambda _, ev=event: self.afficher_details_evenement(ev))
        
        # Ajuster la taille des lignes
        tableau.rowconfigure(0, weight=0)
        tableau.rowconfigure(1, weight=1)
    
    def afficher_vue_jour(self, evenements):
        # Créer un cadre pour le jour
        cadre = tk.Frame(self.main_content, bg=Style.COLORS['background'])
        cadre.pack(fill='both', expand=True, padx=20, pady=20)

        # Créer un canvas + scrollbar pour rendre la timeline scrollable
        canvas = tk.Canvas(cadre, bg='white', highlightthickness=0)
        # Augmentez la taille du canvas pour qu'il soit plus grand
        
        scrollbar = tk.Scrollbar(cadre, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Créer une frame à l'intérieur du canvas
        timeline = tk.Frame(canvas, bg='white')
        timeline_id = canvas.create_window((0, 0), window=timeline, anchor='nw')

        # Mettre à jour la taille du canvas quand la frame change de taille
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        timeline.bind("<Configure>", on_frame_configure)

        # Permettre le scroll avec la molette
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Heures de la journée
        for heure in range(0, 24):
            heure_frame = tk.Frame(timeline, bg='white')
            heure_frame.pack(fill='x')

            # Label de l'heure
            tk.Label(
                heure_frame, 
                text=f"{heure:02d}:00", 
                font=('codec pro extrabold', 9),
                bg='white',
                width=5
            ).pack(side='left')

            # Ligne de temps
            time_slot = tk.Frame(
                heure_frame, 
                bg='white', 
                height=60,
                highlightbackground='#e0e0e0',
                highlightthickness=1
            )
            time_slot.pack(fill='x', expand=True, side='left')
            
            # Événements pour cette heure
            heure_str = self.current_date.strftime(f"%Y-%m-%d {heure:02d}")
            evenements_heure = [
                e for e in evenements 
                if e['date_heure_debut_Evenement'].startswith(heure_str)
            ]
            
            for event in evenements_heure:
                event_card = tk.Frame(
                    time_slot, 
                    bg=event['couleur_evenement'] or Style.COLORS['primary'],
                    padx=5,
                    pady=2,
                    highlightbackground='#e0e0e0',
                    highlightthickness=1
                )
                event_card.pack(fill='x', pady=2)
                
                # Nom de l'événement
                tk.Label(
                    event_card, 
                    text=event['nom_evenement'], 
                    font=('codec pro extrabold', 9),
                    bg=event['couleur_evenement'] or Style.COLORS['primary'],
                    fg='white',
                    anchor='w'
                ).pack(fill='x')
                
                # Bouton pour voir les détails
                event_card.bind("<Button-1>", lambda e, ev=event: self.afficher_details_evenement(ev))
                for child in event_card.winfo_children():
                    child.bind("<Button-1>", lambda e, ev=event: self.afficher_details_evenement(ev))
    
    def afficher_vue_mois(self, evenements):
        # Créer un cadre pour le mois
        cadre = tk.Frame(self.main_content, bg=Style.COLORS['background'])
        cadre.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Obtenir le calendrier du mois
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # En-têtes des jours
        jours_semaine = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        for i, jour in enumerate(jours_semaine):
            tk.Label(
                cadre, 
                text=jour, 
                font=('codec pro extrabold', 10, 'bold'),
                bg=Style.COLORS['background'],
                fg=Style.COLORS['text'],
                width=10,
                height=2
            ).grid(row=0, column=i, sticky="nsew")
        
        # Cases du calendrier
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue  # Jour vide
                
                day_frame = tk.Frame(
                    cadre, 
                    bg='white', 
                    highlightbackground='#e0e0e0', 
                    highlightthickness=1,
                    width=10,
                    height=8
                )
                day_frame.grid(row=week_num, column=day_num, sticky="nsew")
                
                # Numéro du jour
                tk.Label(
                    day_frame, 
                    text=str(day), 
                    font=('codec pro extrabold', 10),
                    bg='white',
                    anchor='ne'
                ).pack(anchor='ne', padx=5, pady=5)
                
                # Événements pour ce jour
                events_frame = tk.Frame(day_frame, bg='white')
                events_frame.pack(fill='both', expand=True)
                
                # Filtrer les événements pour ce jour
                jour_str = self.current_date.replace(day=day).strftime("%Y-%m-%d")
                evenements_jour = [
                    e for e in evenements 
                    if e['date_heure_debut_Evenement'].startswith(jour_str)
                ]
                
                # Afficher les événements (jusqu'à 3)
                for event in evenements_jour[:3]:
                    event_dot = tk.Frame(
                        events_frame, 
                        bg=event['couleur_evenement'] or Style.COLORS['primary'],
                        width=8,
                        height=8
                    )
                    event_dot.pack(side='left', padx=1)
                    
                    # Bouton pour voir les détails
                    event_dot.bind("<Button-1>", lambda e, ev=event: self.afficher_details_evenement(ev))
                
                if len(evenements_jour) > 3:
                    tk.Label(
                        events_frame, 
                        text=f"+{len(evenements_jour)-3} more", 
                        font=('codec pro extrabold', 7),
                        bg='white',
                        fg='gray'
                    ).pack(side='left', padx=2)
        
        # Ajuster la taille des colonnes/lignes
        for i in range(7):
            cadre.columnconfigure(i, weight=1)
        for i in range(len(cal)+1):
            cadre.rowconfigure(i, weight=1)
    
    def afficher_aujourdhui(self):
        self.current_date = datetime.now()
        self.changer_vue('week')
    
    def previous_period(self):
        if self.current_view == 'week':
            self.current_date -= timedelta(weeks=1)
        elif self.current_view == 'month':
            # Aller au mois précédent
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month-1)
        else:  # day
            self.current_date -= timedelta(days=1)
        
        self.afficher_vue()
    
    def next_period(self):
        if self.current_view == 'week':
            self.current_date += timedelta(weeks=1)
        elif self.current_view == 'month':
            # Aller au mois suivant
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month+1)
        else:  # day
            self.current_date += timedelta(days=1)
        
        self.afficher_vue()
    
    def ajouter_evenement_popup_v2(self):
        popup = tk.Toplevel(self)
        popup.title("Ajouter un événement")
        popup.geometry("400x600")
        popup.configure(bg=Style.COLORS['background'])

        # Variables pour le formulaire
        nom_var = tk.StringVar()
        date_debut_var = tk.StringVar(value=self.current_date.strftime("%Y-%m-%d 09:00"))
        date_fin_var = tk.StringVar(value=self.current_date.strftime("%Y-%m-%d 10:00"))
        type_var = tk.StringVar(value="Cours")
        couleur_var = tk.StringVar(value=Style.COLORS['primary'])
        description_var = tk.StringVar()

        # Titre
        tk.Label(
            popup, 
            text="Ajouter un événement", 
            font=('codec pro extrabold', 16, 'bold'), 
            bg=Style.COLORS['background'], 
            fg=Style.COLORS['text']
        ).pack(pady=10)

        # Formulaire
        form_frame = tk.Frame(popup, bg=Style.COLORS['background'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Label(form_frame, text="Nom de l'événement", bg=Style.COLORS['background'], fg=Style.COLORS['text']).pack(anchor='w', pady=(10, 0))
        tk.Entry(form_frame, textvariable=nom_var, font=('codec pro extrabold', 12)).pack(fill='x', pady=(0, 10))

        tk.Label(form_frame, text="Date et heure de début", bg=Style.COLORS['background'], fg=Style.COLORS['text']).pack(anchor='w', pady=(10, 0))
        tk.Entry(form_frame, textvariable=date_debut_var, font=('codec pro extrabold', 12)).pack(fill='x', pady=(0, 10))

        tk.Label(form_frame, text="Date et heure de fin", bg=Style.COLORS['background'], fg=Style.COLORS['text']).pack(anchor='w', pady=(10, 0))
        tk.Entry(form_frame, textvariable=date_fin_var, font=('codec pro extrabold', 12)).pack(fill='x', pady=(0, 10))

        tk.Label(form_frame, text="Type d'événement", bg=Style.COLORS['background'], fg=Style.COLORS['text']).pack(anchor='w', pady=(10, 0))
        type_menu = ttk.Combobox(
            form_frame, 
            textvariable=type_var, 
            values=["Cours", "Examen", "Réunion", "Personnel", "Autre"]
        )
        type_menu.pack(fill='x', pady=(0, 10))

        tk.Label(form_frame, text="Couleur", bg=Style.COLORS['background'], fg=Style.COLORS['text']).pack(anchor='w', pady=(10, 0))
        couleur_menu = ttk.Combobox(
            form_frame, 
            textvariable=couleur_var, 
            values=[
                Style.COLORS['primary'], 
                Style.COLORS['secondary'], 
                "green",  # vert
                "orange",  # orange
                "purple"   # violet
            ]
        )
        couleur_menu.pack(fill='x', pady=(0, 10))

        tk.Label(form_frame, text="Description", bg=Style.COLORS['background'], fg=Style.COLORS['text']).pack(anchor='w', pady=(10, 0))
        description_text = tk.Text(form_frame, height=5, font=('codec pro extrabold', 12))
        description_text.pack(fill='x', pady=(0, 10))

        # Boutons
        btn_frame = tk.Frame(popup, bg=Style.COLORS['background'])
        btn_frame.pack(fill='x', padx=20, pady=10)

        tk.Button(
            btn_frame, 
            text="Annuler", 
            command=popup.destroy,
            bg=Style.COLORS['danger'],
            fg='white',
            font=('codec pro extrabold', 10),
            padx=10,
            pady=5
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame, 
            text="Ajouter", 
            command=lambda: self.ajouter_evenement(
                nom_var.get(),
                date_debut_var.get(),
                date_fin_var.get(),
                type_var.get(),
                couleur_var.get(),
                description_text.get("1.0", tk.END),
                popup
            ),
            bg=Style.COLORS['primary'],
            fg='white',
            font=('codec pro extrabold', 10),
            padx=10,
            pady=5
        ).pack(side='right', padx=5)

        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)
        
    def ajouter_evenement_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Ajouter un événement")
        popup.geometry("400x500")
        
        # Variables pour le formulaire
        nom_var = tk.StringVar()
        date_debut_var = tk.StringVar(value=self.current_date.strftime("%Y-%m-%d 09:00"))
        date_fin_var = tk.StringVar(value=self.current_date.strftime("%Y-%m-%d 10:00"))
        type_var = tk.StringVar(value="Cours")
        couleur_var = tk.StringVar(value=Style.COLORS['primary'])
        description_var = tk.StringVar()
        
        # Formulaire
        tk.Label(popup, text="Nom de l'événement").pack(pady=(10, 0))
        tk.Entry(popup, textvariable=nom_var, font=('codec pro extrabold', 12)).pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(popup, text="Date et heure de début").pack()
        tk.Entry(popup, textvariable=date_debut_var, font=('codec pro extrabold', 12)).pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(popup, text="Date et heure de fin").pack()
        tk.Entry(popup, textvariable=date_fin_var, font=('codec pro extrabold', 12)).pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(popup, text="Type d'événement").pack()
        type_menu = ttk.Combobox(
            popup, 
            textvariable=type_var, 
            values=["Cours", "Examen", "Réunion", "Personnel", "Autre"]
        )
        type_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(popup, text="Couleur").pack()
        couleur_menu = ttk.Combobox(
            popup, 
            textvariable=couleur_var, 
            values=[
                Style.COLORS['primary'], 
                Style.COLORS['secondary'], 
                "green",  # vert
                "orange",  # orange
                "purple"   # violet
            ]
        )
        couleur_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(popup, text="Description").pack()
        description_text = tk.Text(popup, height=5, font=('codec pro extrabold', 12))
        description_text.pack(fill='x', padx=20, pady=(0, 10))
        
        # Boutons
        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(
            btn_frame, 
            text="Annuler", 
            command=popup.destroy,
            bg=Style.COLORS['background'],
            fg=Style.COLORS['text']
        ).pack(side='left')
        
        tk.Button(
            btn_frame, 
            text="Ajouter", 
            command=lambda: self.ajouter_evenement(
                nom_var.get(),
                date_debut_var.get(),
                date_fin_var.get(),
                type_var.get(),
                couleur_var.get(),
                description_text.get("1.0", tk.END),
                popup
            ),
            bg=Style.COLORS['primary'],
            fg='white'
        ).pack(side='right')
        
        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)
    
    def ajouter_evenement(self, nom, date_debut, date_fin, type_event, couleur, description, popup):
        if not nom or not date_debut or not date_fin:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return

        try:
            dt_debut = datetime.strptime(date_debut, "%Y-%m-%d %H:%M")
            dt_fin = datetime.strptime(date_fin, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide. Utilisez YYYY-MM-DD HH:MM")
            return

        if dt_fin <= dt_debut:
            messagebox.showerror("Erreur", "La date de fin doit être postérieure à la date de début")
            return

        # Vérifier le chevauchement avec les événements existants
        evenements = obtenir_evenements(
            self.etudiant_connecte['Identifiant_Etudiant'],
            dt_debut.strftime("%Y-%m-%d 00:00"),
            dt_fin.strftime("%Y-%m-%d 23:59")
        )
        for event in evenements:
            event_debut = datetime.strptime(event['date_heure_debut_Evenement'], "%Y-%m-%d %H:%M")
            event_fin = datetime.strptime(event['date_heure_fin_Evenement'], "%Y-%m-%d %H:%M")
            # Si les intervalles se chevauchent
            if (dt_debut < event_fin and dt_fin > event_debut):
                messagebox.showerror(
                    "Erreur",
                    f"Conflit avec un autre événement :\n{event['nom_evenement']} ({event_debut.strftime('%H:%M')} - {event_fin.strftime('%H:%M')})"
                )
                return

        ajouter_evenement(
            self.etudiant_connecte['Identifiant_Etudiant'],
            nom,
            date_debut,
            date_fin,
            type_event,
            couleur,
            description.strip()
        )

        messagebox.showinfo("Succès", "Événement ajouté avec succès")
        popup.destroy()
        self.afficher_vue()

    def afficher_details_evenement(self, evenement):
        popup = tk.Toplevel(self)
        popup.title("Détails de l'événement")
        popup.geometry("400x400")
        
        # Convertir en objet Evenement
        event_obj = dict_to_evenement(evenement)
        
        # Affichage des détails
        details_frame = tk.Frame(popup, padx=20, pady=20)
        details_frame.pack(fill='both', expand=True)
        
        # Nom et type
        tk.Label(
            details_frame, 
            text=event_obj.nom, 
            font=('codec pro extrabold', 16, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            details_frame, 
            text=f"Type: {event_obj.type_event}", 
            font=('codec pro extrabold', 12)
        ).pack(anchor='w', pady=(0, 10))
        
        # Dates
        tk.Label(
            details_frame, 
            text=f"Début: {event_obj.date_debut.strftime('%A %d %B %Y, %H:%M')}", 
            font=('codec pro extrabold', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        tk.Label(
            details_frame, 
            text=f"Fin: {event_obj.date_fin.strftime('%A %d %B %Y, %H:%M')}", 
            font=('codec pro extrabold', 10)
        ).pack(anchor='w', pady=(0, 10))
        
        # Description
        tk.Label(
            details_frame, 
            text="Description:", 
            font=('codec pro extrabold', 10, 'bold')
        ).pack(anchor='w', pady=(10, 0))
        
        description_text = tk.Text(
            details_frame, 
            height=5, 
            wrap='word',
            font=('codec pro extrabold', 10)
        )
        description_text.insert('1.0', event_obj.description)
        description_text.config(state='disabled')
        description_text.pack(fill='x', pady=(0, 10))
        
        # Boutons
        btn_frame = tk.Frame(details_frame)
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(
            btn_frame, 
            text="Supprimer", 
            command=lambda: self.supprimer_evenement_confirmation(event_obj.id, popup),
            bg=Style.COLORS['danger'],
            fg='white'
        ).pack(side='left')
        
        tk.Button(
            btn_frame, 
            text="Fermer", 
            command=popup.destroy
        ).pack(side='right')
        
        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)
    
    def supprimer_evenement_confirmation(self, event_id, popup):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cet événement?"):
            supprimer_evenement(event_id, self.etudiant_connecte['Identifiant_Etudiant'])
            popup.destroy()
            self.afficher_vue()
    
    def deconnexion(self):
        self.etudiant_connecte = None
        self.afficher_ecran_connexion()
    
    def effacer_interface(self):
        for widget in self.winfo_children():
            widget.destroy()