from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QMenu, 
                             QDialog, QTextEdit, QPushButton)
from PyQt5.QtCore import Qt
from datetime import datetime


# ===== TŘÍDA PRO JEDEN DEN =====
class DayWidget(QWidget):
    """
    Widget pro jeden den - umožňuje context menu (pravé tlačítko)
    """
    #widget je top-level (např. samostatné okno) a musí být spravován ručně reference na parent=None
    def __init__(self, date, parent=None, note_obj=None, reward_obj=None): #tohle jsou parametry, potrebujeme date, a parent je volitelny
        super().__init__(parent) # kdyz neuvedeme parent tak parent je QWidget
        self.date = date  # Uložíme si datum tohoto dne
        self.parent_window = parent  # Odkaz na hlavní okno
        self.note_obj = note_obj
        self.reward_obj = reward_obj 
        
        # Nastav maximální šířku sloupce
        self.setMaximumWidth(200)

        # Layout pro tento den
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Povolit context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_note_detail(self, note):
        """
        Zobrazí detail note v popup okně
        """
        # note = [date, subclass, topic, text]
        date = note[0]
        subclass = note[1]
        topic = note[2]
        text = note[3]
        
        # Vytvoř popup dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Note: {topic}")
        dialog.setModal(True)
        dialog.setMinimumSize(500, 400)
        
        # Layout
        layout = QVBoxLayout()
        
        # Info (datum, subclass)
        info_label = QLabel(f"📅 {date.strftime('%d.%m.%Y')} | 🏷️ {subclass}")
        info_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(info_label)
        
        # Topic (nadpis)
        topic_label = QLabel(topic)
        topic_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(topic_label)
        
        # Text (obsah)
        text_display = QTextEdit()
        text_display.setPlainText(text)
        text_display.setReadOnly(True)  # Jen čtení, ne editace
        layout.addWidget(text_display)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_context_menu(self, position):
        """
        Zobrazí context menu při pravém kliknutí
        """
        
        # Vytvoř menu
        menu = QMenu(self)
        
        #Styling
        menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid white;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #3D3D3D;
            }
    """)

        
        # Přidej akce (možnosti)
        add_task_action = menu.addAction("Add Task")
        add_note_action = menu.addAction("Add Note")    
        add_reward_action = menu.addAction("Add Reward")
        add_review_action = menu.addAction("Review day")
        add_review_rewards_action = menu.addAction("Review rewards")
        
        # Zobraz menu a čekej na kliknutí
        action = menu.exec_(self.mapToGlobal(position))
        
        # Zjisti co uživatel klikl
        if action == add_task_action:
            self.parent_window.add_task_for_date(self.date)
        elif action == add_note_action:
            self.parent_window.add_note_for_date(self.date)
        elif action == add_reward_action:
            self.parent_window.add_reward_for_date(self.date)
        elif action == add_review_action:
            self.parent_window.review_day(self.date)
        elif action == add_review_rewards_action:  
            self.parent_window.review_rewards(self.date)


    def update_content(self, date, day_name, all_tasks_obj, note_obj=None, reward_obj=None):
        """
        Aktualizuje obsah widgetu (datum + tasky) pro nový týden
        
        Args:
            date: Nové datum pro tento widget
            day_name: Název dne (Mon, Tue, ...)
            all_tasks_obj: Odkaz na All_tasks objekt
        """
        self.note_obj = note_obj 
        self.reward_obj = reward_obj
        # Zakaž překreslování během aktualizace
        self.setUpdatesEnabled(False)

        # Aktualizuj uložené datum
        self.date = date
        
        # Vyčisti layout (smaž všechny widgety)
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Formátuj datum
        date_str = f"{date.day}.{date.month}"

        # Zjisti jestli je to dnešní den
        today = datetime.now().date()
        is_today = (date.date() == today)
        
        # Vytvoř nový day_label
        day_label = QLabel(f"{day_name}\n{date_str}")
        day_label.setAlignment(Qt.AlignCenter)
        
        # Styling - zvýrazni dnešní den
        if is_today:
            day_label.setStyleSheet("""
                background-color: white;
                color: black;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
            """)
        else:
            day_label.setStyleSheet("color: white; font-size: 18px;")

        self.layout.addWidget(day_label)
        
        # Získej tasky pro tento den
        tasks_for_day = self.get_tasks_for_date(date, all_tasks_obj)
        
        # Vytvoř label pro každý task
        for task in tasks_for_day:
            task_name = task[0]
            task_hours = task[3]
            
            
            # Zkontroluj jestli má review
            has_review = False
            if len(task) > 5:
                review = task[5]
                if isinstance(review, list) and len(review) > 0:
                    has_review = any(r.strip() for r in review if r)
            
            # Ikona podle review
            icon = "✅" if has_review else "•"
            
            # Zkrať název
            max_length = 18    
            display_name = task_name if len(task_name) <= max_length else task_name[:max_length] + "..."
            
            task_label = QLabel(f"{icon} {display_name}\n   ({task_hours}h)")  
            task_label.setAlignment(Qt.AlignLeft)
            task_label.setStyleSheet("color: lightgray; font-size: 14px; padding-left: 10px;")
            task_label.setToolTip(task_name)
            self.layout.addWidget(task_label)

        # ===== ZOBRAZENÍ NOTES PRO TENTO DEN =====
        if self.note_obj:  # Kontrola jestli máme note_obj
            notes_for_day = self.get_notes_for_date(date, self.note_obj)
            
            # Vytvoř label pro každou note
            for note in notes_for_day:
                note_topic = note[2]  # topic je na indexu 2
                
                # Zkrať topic pokud je moc dlouhý
                max_length = 18
                display_topic = note_topic if len(note_topic) <= max_length else note_topic[:max_length] + "..."
                
                # Note label (jiná barva - žlutá/oranžová)
                note_label = QLabel(f"📝 {display_topic}")
                note_label.setAlignment(Qt.AlignLeft)
                note_label.setStyleSheet("color: #FFA500; font-size: 14px; padding-left: 10px;")
                note_label.setToolTip(note_topic)
                
                # Ulož si note data do labelu (abychom je mohli zobrazit při kliknutí)
                note_label.setProperty("note_data", note)
                
                # Povolit kliknutí na label
                note_label.setCursor(Qt.PointingHandCursor)  # Kurzor se změní na ruku
                note_label.mousePressEvent = lambda event, n=note: self.show_note_detail(n)
                
                self.layout.addWidget(note_label)
            
        # ===== ZOBRAZENÍ REWARDS PRO TENTO DEN =====
        if self.reward_obj:
            rewards_for_day = self.get_rewards_for_date(date, self.reward_obj)
        
            # Vytvoř label pro každou reward
            for reward in rewards_for_day:
                reward_name = reward[1]  # reward_name je na indexu 1
                reward_time = reward[2]  # time
                reward_finished = reward[3]  # finished
                
                is_reviewed = False
                if len(reward) > 4:
                    actual_time = reward[4]  # actual_time
                    # Je reviewed pokud má actual_time NEBO je finished
                    is_reviewed = reward_finished or (actual_time is not None and actual_time != reward_time)
                
                # Ikona podle stavu
                if is_reviewed:
                    icon = "✅"  # Zreviewovaná (splněná NEBO má actual_time)
                else:
                    icon = "🎁"  # Nezreviewovaná
                
                # Zkrať název pokud je moc dlouhý
                max_length = 18  # O trochu kratší kvůli ikoně
                display_reward = reward_name if len(reward_name) <= max_length else reward_name[:max_length] + "..."
                
                # Reward label (zelená barva)
                reward_label = QLabel(f"{icon} {display_reward}\n ({reward_time}h)")
                reward_label.setAlignment(Qt.AlignLeft)
                reward_label.setStyleSheet("color: #00FF00; font-size: 14px; padding-left: 10px;")
                reward_label.setToolTip(reward_name)
                
                self.layout.addWidget(reward_label)
        
        # Prostor pod tasky a notes
        self.layout.addStretch()

        # Povol překreslování a aktualizuj
        self.setUpdatesEnabled(True)
        self.update()

        
    def get_tasks_for_date(self, date, all_tasks_obj):
        """
        Vrátí tasky pro dané datum
        """
        tasks_for_day = []
        
        for task in all_tasks_obj.list_of_all_tasks_objects:
            task_date = task[2]
            
            if isinstance(task_date, datetime):
                task_date = task_date.date()
            
            if task_date == date.date():
                tasks_for_day.append(task)
        
        return tasks_for_day
    
    def get_notes_for_date(self, date, note_obj):
        """
        Vrátí notes pro dané datum
        """
        notes_for_day = []
        
        for note in note_obj.list_of_all_notes_objects:
            # note[0] = date (první prvek)
            note_date = note[0]
            
            if isinstance(note_date, datetime):
                note_date = note_date.date()
            
            if note_date == date.date():
                notes_for_day.append(note)
        
        return notes_for_day
    
    def get_rewards_for_date(self, date, reward_obj):
        """
        Vrátí rewards pro dané datum
        """
        rewards_for_day = []
        
        for reward in reward_obj.list_of_all_reward_objects:
            # reward[0] = date_of_creation
            reward_date = reward[0]
            
            if isinstance(reward_date, datetime):
                reward_date = reward_date.date()
            
            if reward_date == date.date():
                rewards_for_day.append(reward)
        
        return rewards_for_day