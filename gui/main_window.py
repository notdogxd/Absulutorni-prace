from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QScrollArea, QDialog, QMenu)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime, timedelta

# Import našich vlastních tříd
from .day_widget import DayWidget
from .add_task_dialog import AddTaskDialog
from .add_note_dialog import AddNoteDialog
from .add_reward_dialog import AddRewardDialog
from .set_goals_dialog import SetGoalsDialog 

# Import backendu
from models.settings import Settings
from models.all_tasks import All_tasks
from models.goal import Goal
from models.notes_class import Note
from models.reward import Reward
from models.cycles_manager import CyclesManager  
from gui.review_day_dialog import ReviewDayDialog


# ===== HLAVNÍ OKNO =====
class WeekView(QMainWindow):
    """
    Hlavní okno aplikace - zobrazuje týdenní kalendář (7 dní)
    S navigací Previous/Next pro přepínání mezi týdny (1-12)
    """

    def get_rotated_days(self, start_weekday):
        """
        Rotuje názvy dnů podle toho, kterým dnem začal uživatel
        
        Args:
            start_weekday (int): Den v týdnu kdy začal (0=Mon, 1=Tue, ..., 6=Sun)
            
        Returns:
            list: Rotovaný list dnů (např. ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"])
        
        Příklad:
            Pokud uživatel začal ve středu (2):
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            → ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"]
        """
        all_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return all_days[start_weekday:] + all_days[:start_weekday]
    
    def get_week_dates(self, week_number):
        """
        Vypočítá konkrétní data (datetime objekty) pro daný týden
        
        Args:
            week_number (int): Číslo týdne (1-12)
            
        Returns:
            list: List 7 datetime objektů
        """
        # Získej start_date z aktivního cyklu
        active_cycle = self.cycles_manager.get_active_cycle()
        
        if not active_cycle:
            # Žádný aktivní cyklus - použij dnešek jako fallback
            from datetime import datetime
            start_date = datetime.now()
        else:
            start_date = active_cycle['start_date']
        
        # Kolik dní od start_date je začátek tohoto týdne?
        days_offset = (week_number - 1) * 7
        
        # První den tohoto týdne
        week_start = start_date + timedelta(days=days_offset)
        
        # Vytvoř list 7 po sobě jdoucích dat
        dates = []
        for i in range(7):
            date = week_start + timedelta(days=i)
            dates.append(date)
        
        return dates
    
        
    def update_week_display(self):
        """
        Aktualizuje zobrazení dnů a dat po změně týdne (Next/Previous)
        """
        # Získej nová data pro aktuální týden
        week_dates = self.get_week_dates(self.current_week)
    
         # Aktualizuj každý DayWidget (datum + tasky)
        for i, day_widget in enumerate(self.day_widgets):
            date = week_dates[i]
            day_name = self.days[i]
        
            # Aktualizuj obsah widgetu
            day_widget.update_content(date, day_name, self.all_tasks, self.note, self.reward)
    
    def __init__(self):
        """
        Inicializace hlavního okna - nastavení GUI, načtení settings, zobrazení týdne
        """
        super().__init__()
    
        # ===== NAČTENÍ CYCLES MANAGER =====
        self.cycles_manager = CyclesManager()
        
        # Zkontroluj a sprav cykly
        self.handle_cycles()
        
        # ===== NAČTENÍ SETTINGS =====
        self.settings = Settings()

        # Načti backend objekty
        self.all_tasks = All_tasks()
        self.goal = Goal(self.all_tasks)
        self.note = Note()
        self.reward = Reward()

        
        # Spočítej na kterém týdnu jsme (1-12)
        self.current_week = self.calculate_current_week()
        
        # ===== NASTAVENÍ HLAVNÍHO OKNA =====
        self.setWindowTitle("12 Week Planner")
        self.setGeometry(0, 0, 1920, 1080) 
        self.setStyleSheet("""
            background-color: black;
            color: white;
            font-size: 16px;
        """)
        
        # ===== VYTVOŘENÍ CENTRAL WIDGET A MAIN LAYOUT =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()  # Vertikální layout (věci pod sebou)

        # ===== HORNÍ LIŠTA (Previous, Week X, Next) =====
        
        # Previous button (vlevo)
        self.previous_button = QPushButton("Previous")
        self.previous_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")    
        self.previous_button.clicked.connect(self.previous_week)

        # Week label (uprostřed)
        self.week_label = QLabel(f"Week {self.current_week}")
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setStyleSheet("color: white; font-size: 24px;")

        # Next button (vpravo)
        self.next_button = QPushButton("Next")
        self.next_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        self.next_button.clicked.connect(self.next_week)

        # Horizontální layout pro horní lištu
        top_layout = QHBoxLayout()

        
        # Hamburger menu button (vlevo)
        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(80, 40)
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 32px;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
                border-radius: 5px;
            }
        """)
        self.menu_button.clicked.connect(self.show_hamburger_menu)
        top_layout.addWidget(self.menu_button)

        # Spacing mezi menu a buttons
        top_layout.addSpacing(20)
        top_layout.addWidget(self.previous_button)
        top_layout.addWidget(self.week_label)
        top_layout.addWidget(self.next_button)
        
        # Přidej horní lištu do main_layout
        main_layout.addLayout(top_layout)

        # ===== DNY V TÝDNU (Mon-Sun s datumy) =====
        
        # Kontejner pro dny (horizontální - vedle sebe)
        days_container = QHBoxLayout()

        # Zjisti který den byl start a rotuj dny
        active_cycle = self.cycles_manager.get_active_cycle()
        if active_cycle:
            start_weekday = active_cycle['start_date'].weekday()
        else:
            start_weekday = 0  # Monday default

        self.days = self.get_rotated_days(start_weekday)  # Ulož jako self.days
        days = self.days  # Použij v loopu

        
        # Získej datumy pro aktuální týden
        week_dates = self.get_week_dates(self.current_week)

        # List pro uložení day_labels (abychom je mohli aktualizovat)
        self.day_labels = []  

        # List pro uložení day_widgets (abychom mohli aktualizovat tasky)
        self.day_widgets = [] 
        
        # Vytvoř sloupec pro každý den
        for i, day in enumerate(days):
            date = week_dates[i]
            
            # 1. Vytvoř widget pro den
            day_widget = DayWidget(date, self, self.note, self.reward)

            # 2. Ulož si widget pro pozdější aktualizaci
            self.day_widgets.append(day_widget)
            
            # 3. ZAVOLEJ update_content
            # Tato metoda se postará o vytvoření nadpisu dne, data, úkolů, notes i rewards.
            day_widget.update_content(date, day, self.all_tasks, self.note, self.reward)
        
            # 4. Přidej widget do kontejneru
            days_container.addWidget(day_widget)
            
            # 5. Přidej vertikální čáru mezi dny (pokud to není poslední den)
            if i < len(days) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.VLine)
                separator.setStyleSheet("color: white;")
                days_container.addWidget(separator)
      
            # ===== SCROLL AREA =====
        # Vytvoř widget pro days_container
        days_widget = QWidget()
        days_widget.setLayout(days_container)
        
        # Vytvoř scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(days_widget)
        scroll_area.setWidgetResizable(True)  # Důležité - widget se přizpůsobí
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Jen vertikální scroll
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: black; }")
        
        # Přidej scroll area do main_layout (místo days_container)
        main_layout.addWidget(scroll_area)

        # ===== FINALIZACE =====
        central_widget.setLayout(main_layout)

        # Na Week 1 je Previous vypnutý (nemůžeme jít zpět)
        if self.current_week <= 1:
            self.previous_button.setEnabled(False)

        self.update_week_display()

    def archive_cycle_manually(self):
        """
        Manuální archivace cyklu
        """
        from PyQt5.QtWidgets import QMessageBox
        
        active_cycle = self.cycles_manager.get_active_cycle()
        
        if not active_cycle:
            QMessageBox.warning(self, "No Active Cycle", "No active cycle to archive!")
            return
        
        cycle_id = active_cycle['id']
        start_date = active_cycle['start_date']
        end_date = active_cycle['end_date']

        days_left = (end_date - datetime.now()).days

        # Formátuj na evropský formát (dd.mm.yyyy)
        start_date_str = start_date.strftime("%d.%m.%Y")
        end_date_str = end_date.strftime("%d.%m.%Y")

        reply = QMessageBox.question(
            self,
            "Archive Cycle",
            f"Archive Cycle #{cycle_id}\n\n"
            f"Period: {start_date_str} - {end_date_str}\n" 
            f"Days remaining: {days_left}\n\n"
            f"Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        success = self.cycles_manager.archive_current_cycle()
        
        if not success:
            QMessageBox.critical(self, "Error", "Archive failed!")
            return
        
        new_cycle = self.cycles_manager.create_new_cycle()
        
        QMessageBox.information(
            self,
            "Success",
            f"Cycle #{cycle_id} archived!\n\n"
            f"New Cycle #{new_cycle['id']} started."
        )
        
        # Reload
        self.all_tasks = All_tasks()
        self.goal = Goal(self.all_tasks)
        self.note = Note()
        self.reward = Reward()
        self.settings.set_goals_completed(False)
        
        self.current_week = 1
        self.week_label.setText("Week 1")
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(True)
        
        self.update_week_display()
        
        QTimer.singleShot(100, self.show_goals_dialog)

    def show_hamburger_menu(self):
        """
        Zobrazí hamburger menu (☰)
        """
        
        # Vytvoř menu
        menu = QMenu(self)
        
        # Styling
        menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 2px solid white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QMenu::item {
                padding: 10px 40px 10px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #3D3D3D;
            }
            QMenu::separator {
                height: 2px;
                background-color: white;
                margin: 8px 0px;
            }
        """)
        
        # ===== CYCLES SECTION =====
        cycles_header = menu.addAction("📊 CYCLES")
        cycles_header.setEnabled(False)  # Jen nadpis
        
        archive_action = menu.addAction("   Archive Current Cycle")
        archive_action.triggered.connect(self.archive_cycle_manually)
        
        history_action = menu.addAction("   Cycles History")
        history_action.triggered.connect(self.show_cycles_history)
        
        stats_action = menu.addAction("   Statistics")
        stats_action.triggered.connect(self.show_statistics)
        
        menu.addSeparator()
        
        # ===== MANAGE SECTION =====
        manage_header = menu.addAction("⚙️ MANAGE")
        manage_header.setEnabled(False)
        
        goals_action = menu.addAction("   Goals")
        goals_action.triggered.connect(self.manage_goals)
        
        tasks_action = menu.addAction("   Tasks")
        tasks_action.triggered.connect(self.manage_tasks)
        
        notes_action = menu.addAction("   Notes")
        notes_action.triggered.connect(self.manage_notes)
        
        rewards_action = menu.addAction("   Rewards")
        rewards_action.triggered.connect(self.manage_rewards)
        
        menu.addSeparator()
        
        # ===== VIEW SECTION =====
        view_header = menu.addAction("👁️ VIEW")
        view_header.setEnabled(False)
        
        current_week_action = menu.addAction("   Go to Current Week")
        current_week_action.triggered.connect(self.go_to_current_week)
        
        refresh_action = menu.addAction("   Refresh")
        refresh_action.triggered.connect(self.update_week_display)
        
        menu.addSeparator()
        
        # ===== ABOUT =====
        about_action = menu.addAction("❓ About")
        about_action.triggered.connect(self.show_about)
        
        # Zobraz menu pod hamburger buttonem
        button_pos = self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft())
        menu.exec_(button_pos)
    
    def show_statistics(self):
        """
        Zobrazí statistiky
        """
        from gui.statistics_dialog import StatisticsDialog
        
        dialog = StatisticsDialog(self.cycles_manager, self.all_tasks, self.goal, self)
        dialog.exec_()

    def calculate_current_week(self):
        """
        Spočítá aktuální týden v cyklu (1-12)
        
        Returns:
            int: Číslo týdne (1-12)
        """
        active_cycle = self.cycles_manager.get_active_cycle()
        
        if not active_cycle:
            return 1  # Default
        
        start_date = active_cycle['start_date']
        today = datetime.now()
        
        days_since_start = (today - start_date).days
        
        # Spočítej týden (1-12)
        week = (days_since_start // 7) + 1
        
        # Omez na 1-12
        if week < 1:
            week = 1
        if week > 12:
            week = 12
        
        return week

    def handle_cycles(self):
        """
        Správa cyklů při startu aplikace
        
        Logika:
        1. Zkontroluj jestli existuje aktivní cyklus
        2. Pokud ne → vytvoř nový
        3. Pokud ano → zkontroluj jestli už neuplynulo 12 týdnů
        4. Pokud uplynulo → archivuj a vytvoř nový
        """
        print("\n" + "="*50)
        print("🔄 CYCLES MANAGER - Kontrola cyklů")
        print("="*50)
        
        # 1. Potřebujeme nový cyklus?
        if self.cycles_manager.needs_new_cycle():
            print("⚠️ Potřeba nový cyklus")
            
            # Zjisti jestli existuje nějaký aktivní (k archivaci)
            active = self.cycles_manager.get_active_cycle()
            
            if active:
                print(f"📦 Archivuji cyklus #{active['id']}...")
                
                # Zeptej se uživatele
                from PyQt5.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    None,
                    "New Cycle",
                    f"12 weeks have passed since {active['start_date'].date()}.\n\n"
                    "Archive current cycle and start a new one?\n\n"
                    "Your data will be saved to archive.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # Archivuj
                    success = self.cycles_manager.archive_current_cycle()
                    
                    if success:
                        print("✅ Archivace dokončena")
                        
                        # Vytvoř nový cyklus
                        new_cycle = self.cycles_manager.create_new_cycle()
                        print(f"✅ Nový cyklus #{new_cycle['id']} vytvořen")
                        
                        # Info okno
                        QMessageBox.information(
                            None,
                            "New Cycle Started",
                            f"Cycle #{new_cycle['id']} started!\n\n"
                            f"Duration: {new_cycle['start_date'].date()} - {new_cycle['end_date'].date()}\n\n"
                            "Set your goals for the next 12 weeks!"
                        )
                    else:
                        print("❌ Archivace selhala")
                else:
                    print("⏸️ Uživatel odmítl archivaci - ponecháváme starý cyklus")
            
            else:
                # Žádný aktivní cyklus - první spuštění
                print("🆕 První spuštění - vytváření prvního cyklu")
                new_cycle = self.cycles_manager.create_new_cycle()
                print(f"✅ Cyklus #{new_cycle['id']} vytvořen")
        
        else:
            # Všechno OK - cyklus běží
            active = self.cycles_manager.get_active_cycle()
            print(f"✅ Aktivní cyklus #{active['id']}")
            print(f"   Start: {active['start_date'].date()}")
            print(f"   End: {active['end_date'].date()}")
            
            # Kolik dní zbývá?
            from datetime import datetime
            days_left = (active['end_date'] - datetime.now()).days
            print(f"   Zbývá: {days_left} dní")
        
        print("="*50 + "\n")    
            
    def open_management_dialog(self):
        """
        Otevře management dialog
        """
        from .management_dialog import ManagementDialog
        
        dialog = ManagementDialog(self, self.all_tasks, self.goal, self.note, self.reward)
        dialog.exec_()
        
        # Refresh GUI po zavření dialogu
        self.update_week_display()

    def next_week(self):
        """
        Handler pro Next button - přepne na další týden
        """
        # Zvýš číslo týdne
        self.current_week += 1
        
        # Aktualizuj text labelu
        self.week_label.setText(f"Week {self.current_week}")
        
        # Zapni Previous (už nejsme na Week 1)
        self.previous_button.setEnabled(True)
        
        # Na Week 12 vypni Next (nemůžeme jít dál)
        if self.current_week >= 12:
            self.next_button.setEnabled(False)
        
        # Aktualizuj data dnů
        self.update_week_display()

    def previous_week(self):
        """
        Handler pro Previous button - přepne na předchozí týden
        """
        # Sniž číslo týdne
        self.current_week -= 1
        
        # Aktualizuj text labelu
        self.week_label.setText(f"Week {self.current_week}")
        
        # Zapni Next (už nejsme na Week 12)
        self.next_button.setEnabled(True)
        
        # Na Week 1 vypni Previous (nemůžeme jít zpět)
        if self.current_week <= 1:
            self.previous_button.setEnabled(False)
        
        # Aktualizuj data dnů
        self.update_week_display()
    
    def add_task_for_date(self, date):
        """
        Otevře popup pro přidání tasku k danému datu
        """
        # Vytvoř a zobraz dialog
        dialog = AddTaskDialog(date, self, self.goal.list_of_all_goals_objects)
        
        # Čekej na odpověď (uživatel klikne Save nebo Cancel)
        result = dialog.exec_()
        
        # Pokud user klikl Save (ne Cancel)
        if result == QDialog.Accepted:
            # Získej data z dialogu
            task_data = dialog.task_data
            
            # Ulož task do backendu
            self.all_tasks.add_new_task(task_data)
            
            print(f"✅ Task uložen: {task_data[0]}")
            
            # Refresh GUI - aktualizuj zobrazení aktuálního týdne
            self.update_week_display()


    def add_note_for_date(self, date):
        """
        Otevře popup pro přidání note k danému datu
        """
        # Vytvoř a zobraz dialog
        dialog = AddNoteDialog(date, self)
        
        # Čekej na odpověď
        result = dialog.exec_()
        
        # Pokud user klikl Save
        if result == QDialog.Accepted:
            # Získej data
            note_data = dialog.note_data
            
            # Ulož note do backendu
            self.note.create_note(note_data)
            
            print(f"✅ Note uložena: {note_data[2]}")  # topic

            self.update_week_display() 

    def add_reward_for_date(self, date):
        """
        Otevře popup pro přidání reward k danému datu
        """
        # Vytvoř a zobraz dialog
        dialog = AddRewardDialog(date, self)
        
        # Čekej na odpověď
        result = dialog.exec_()
        
        # Pokud user klikl Save
        if result == QDialog.Accepted:
            # Získej data
            reward_data = dialog.reward_data
            
            # Ulož reward do backendu
            self.reward.add_reward(reward_data)
            
            print(f"✅ Reward uložena: {reward_data[1]}")
            
            # Refresh GUI
            self.update_week_display()

    def review_day(self, date):
        """
        Otevře review dialog pro daný den
        """
        # Získej tasky pro tento den
        tasks_for_day = []
        task_indices = []
        
        for i, task in enumerate(self.all_tasks.list_of_all_tasks_objects):
            task_date = task[2]  # Index 2 = date
            
            # Porovnej datumy
            if isinstance(task_date, datetime):
                task_date = task_date.date()
            
            if task_date == date.date():
                tasks_for_day.append(task)
                task_indices.append(i)
        
        # Zobraz dialog
        dialog = ReviewDayDialog(date, tasks_for_day, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Ulož reviews do tasků
            for task_index, score, went_well, didnt_work, improve in dialog.review_data:
                # Najdi skutečný index v all_tasks
                real_index = task_indices[task_index]
                task = self.all_tasks.list_of_all_tasks_objects[real_index]
                
                # Uprav task: [name, subclass, date, hours, score, review]
                task[4] = score  # Score (0-10)
                task[5] = [went_well, didnt_work, improve]  # Review - 3 části
            
            # Ulož změny
            self.all_tasks.update_data_frame()
            
            print(f"✅ Reviews uloženy pro {len(dialog.review_data)} tasků")
            
            # Refresh GUI
            self.update_week_display()

    def review_rewards(self, date):
        """
        Otevře review dialog pro rewards daného dne
        """
        from gui.review_rewards_dialog import ReviewRewardsDialog
        
        # Získej rewards pro tento den
        rewards_for_day = []
        reward_indices = []
        
        for i, reward in enumerate(self.reward.list_of_all_reward_objects):
            reward_date = reward[0]  # Index 0 = date
            
            # Porovnej datumy
            from datetime import datetime
            if isinstance(reward_date, datetime):
                reward_date = reward_date.date()
            
            if reward_date == date.date():
                rewards_for_day.append(reward)
                reward_indices.append(i)
        
        # Zobraz dialog
        dialog = ReviewRewardsDialog(date, rewards_for_day, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Ulož reviews do rewards
            for reward_index, completed, actual_time in dialog.review_data:
                # Najdi skutečný index
                real_index = reward_indices[reward_index]
                reward = self.reward.list_of_all_reward_objects[real_index]
                
                # Uprav reward: [date, name, time, finished, actual_time]
                reward[3] = completed  # Finished
                
                # Přidej actual_time pokud ještě nemá
                if len(reward) < 5:
                    reward.append(actual_time)
                else:
                    reward[4] = actual_time
            
            # Ulož změny
            self.reward.update_data_frame()
            
            print(f"✅ Reward reviews uloženy pro {len(dialog.review_data)} rewards")
            
            # Refresh GUI
            self.update_week_display()

    def show_goals_dialog(self):
        """
        Zobrazí dialog pro nastavení goals
        """
        dialog = SetGoalsDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            goals = dialog.goals_data
            
            # Získej cycle dates z CyclesManager
            active_cycle = self.cycles_manager.get_active_cycle()
            
            if not active_cycle:
                print("❌ Žádný aktivní cyklus!")
                return
            
            cycle_start = active_cycle['start_date']  
            cycle_end = active_cycle['end_date']
            
            # Ulož každý goal do backendu
            for goal_list in goals:
                goal_data = [
                    goal_list[0],   # 0 - goal_name
                    goal_list[1],   # 1 - subclass
                    goal_list[2],   # 2 - timer
                    goal_list[3],   # 3 - average_score
                    cycle_start,    # 4 - date_of_creation
                    False,          # 5 - checked
                    cycle_end,      # 6 - end_date
                    False           # 7 - completed
                ]
                self.goal.add_goal(goal_data)
                print(f"✅ Goal: {goal_list[0]} | {goal_list[2]}h | score {goal_list[3]}")
            
            # Označ že goals byly nastaveny
            self.settings.set_goals_completed(True)
            
            # Zobraz potvrzení
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Goals Set!",
                f"You've set {len(goals)} goals for the next 12 weeks.\n\n"
                "Stay focused and achieve them! 💪"
            )
            
    def has_active_goals(self):
        """
        Zkontroluje jestli má uživatel nastavené goals pro aktuální cyklus
        
        Returns:
            bool: True pokud má goals, False pokud nemá
        """
        
        if not self.goal.list_of_all_goals_objects:
            return False
        
        # Zkontroluj jestli má alespoň 1 goal
        if len(self.goal.list_of_all_goals_objects) < 1:
            return False
        
        return True
    
    def get_current_cycle_goals(self):
        """
        Vrátí goals pro aktuální cyklus
        """
        # Získej start_date z aktivního cyklu
        active_cycle = self.cycles_manager.get_active_cycle()
        
        if not active_cycle:
            return []  # Žádný aktivní cyklus
        
        current_start = active_cycle['start_date']  
        
        # Filtruj goals podle start_date
        current_goals = []
        for goal in self.goal.list_of_all_goals_objects:
            # Starý formát - přeskoč
            if len(goal) < 8:
                continue
            
            # Rozšířený formát: date_of_creation je na indexu 4
            goal_start_date = goal[4]
            
            # Porovnej start_date (jen datum, ne čas)
            if isinstance(goal_start_date, datetime):
                goal_start_date = goal_start_date.date()
            
            if isinstance(current_start, datetime):
                current_start_date = current_start.date()
            else:
                current_start_date = current_start
            
            # Je tento goal z aktuálního cyklu?
            if goal_start_date == current_start_date:
                current_goals.append(goal)
        
        return current_goals
    def show_cycles_history(self):
        """
        Zobrazí historii všech cyklů
        """
        from gui.cycles_history_dialog import CyclesHistoryDialog
        
        dialog = CyclesHistoryDialog(self.cycles_manager, self)
        dialog.exec_()

    def show_statistics(self):
        """
        Zobrazí statistiky
        """
        from gui.statistics_dialog import StatisticsDialog
        
        dialog = StatisticsDialog(self.cycles_manager, self.all_tasks, self.goal, self)
        dialog.exec_()

    def manage_goals(self):
        self.open_management_dialog()

    def manage_tasks(self):
        self.open_management_dialog()

    def manage_notes(self):
        self.open_management_dialog()

    def manage_rewards(self):
        self.open_management_dialog()

    def go_to_current_week(self):
        self.current_week = self.calculate_current_week()
        self.week_label.setText(f"Week {self.current_week}")
        self.previous_button.setEnabled(self.current_week > 1)
        self.next_button.setEnabled(self.current_week < 12)
        self.update_week_display()

    def show_about(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About",
            "12 Week Planner v1.0\n\n"
            "Built with PyQt5 & Python 🐍"
        )