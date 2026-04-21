"""
Statistics Dialog - zobrazení statistik s 4 taby
"""
import math
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QWidget, QComboBox,
                             QScrollArea, QFrame, QProgressBar)
from PyQt5.QtCore import Qt
from models.statistics import Statistics


class StatisticsDialog(QDialog):
    """
    Dialog se statistikami - 4 taby: Overview, Categories, Trends, Goals
    """
    
    def __init__(self, cycles_manager, all_tasks, goals, parent=None):
        super().__init__(parent)
        
        # Data
        self.cycles_manager = cycles_manager
        self.all_tasks = all_tasks
        self.goals = goals
        
        # Statistický engine
        self.stats = Statistics(cycles_manager, all_tasks, goals)
        
        # Aktuální období
        self.current_period = "current_week"
        
        self.setWindowTitle("Statistics")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        """
        Vytvoří UI
        """
        main_layout = QVBoxLayout()
        
        # ===== HEADER =====
        title = QLabel("📊 Statistics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # ===== TIME PERIOD SELECTOR =====
        period_layout = QHBoxLayout()
        
        period_label = QLabel("Time Period:")
        period_label.setStyleSheet("color: white; font-size: 14px;")
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Current Week",
            "Last 6 Weeks",
            "Current Cycle (12 weeks)",
            "All Time"
        ])
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: black;
                color: white;
                border: 1px solid white;
                padding: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: black;
                color: white;
                selection-background-color: #3D3D3D;
            }
        """)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()
        
        main_layout.addLayout(period_layout)
        
        # ===== TABS =====
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid white;
                background-color: black;
            }
            QTabBar::tab {
                background-color: black;
                color: white;
                border: 1px solid white;
                padding: 10px 20px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: #3D3D3D;
                font-weight: bold;
            }
        """)
        
        # Tab 1: Overview
        self.overview_tab = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.overview_tab, "Overview")
        
        # Tab 2: Categories
        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tabs.addTab(self.categories_tab, "Categories")
        
        # Tab 3: Trends
        self.trends_tab = QWidget()
        self.setup_trends_tab()
        self.tabs.addTab(self.trends_tab, "Trends")
        
        # Tab 4: Goals
        self.goals_tab = QWidget()
        self.setup_goals_tab()
        self.tabs.addTab(self.goals_tab, "Goals")
        
        main_layout.addWidget(self.tabs)
        
        # ===== CLOSE BUTTON =====
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                padding: 10px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        main_layout.addWidget(close_btn)
        
        self.setLayout(main_layout)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: black;
            }
        """)
    
    def on_period_changed(self, index):
        """
        Handler pro změnu období
        """
        periods = ["current_week", "last_6_weeks", "current_cycle", "all_time"]
        self.current_period = periods[index]
        
        # Refresh všechny taby
        self.refresh_overview()
        self.refresh_categories()
        # Trends a Goals jsou nezávislé na období
    
    # ===== TAB 1: OVERVIEW =====
    
    def setup_overview_tab(self):
        """
        Vytvoří Overview tab
        """
        layout = QVBoxLayout()
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.overview_content = QWidget()
        self.overview_layout = QVBoxLayout()
        
        self.refresh_overview()
        
        self.overview_content.setLayout(self.overview_layout)
        scroll.setWidget(self.overview_content)
        
        layout.addWidget(scroll)
        self.overview_tab.setLayout(layout)
    
    def refresh_overview(self):
        """
        Refresh Overview tab obsah
        """
        # Vyčisti layout
        while self.overview_layout.count():
            child = self.overview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Získej data
        overview = self.stats.get_overview_stats(self.current_period)
        best = self.stats.get_best_categories(self.current_period, limit=3)
        worst = self.stats.get_worst_categories(self.current_period, limit=3)
        
        # ===== OVERALL STATS =====
        section_label = QLabel("📈 OVERALL STATS")
        section_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 20px;")
        self.overview_layout.addWidget(section_label)
        
        stats_text = f"""
        Total Tasks: {overview['total_tasks']}
        Total Hours: {overview['total_hours']}h
        Average Score: {overview['avg_score']}/10
        Reviewed: {overview['reviewed_count']}/{overview['total_tasks']} ({overview['review_rate']}%)
                """
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("color: white; font-size: 14px; margin-left: 20px;")
        self.overview_layout.addWidget(stats_label)
        
        # ===== BEST PERFORMING =====
        if best:
            section_label = QLabel("🏆 BEST PERFORMING")
            section_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 20px;")
            self.overview_layout.addWidget(section_label)
            
            for cat in best:
                cat_text = f"{cat['category']}: {cat['avg_score']}/10 avg ({cat['tasks_count']} tasks, {cat['hours']}h)"
                cat_label = QLabel(f"• {cat_text}")
                cat_label.setStyleSheet("color: #00FF00; font-size: 14px; margin-left: 20px;")
                self.overview_layout.addWidget(cat_label)
        
        # ===== NEEDS ATTENTION =====
        if worst:
            section_label = QLabel("⚠️ NEEDS ATTENTION")
            section_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 20px;")
            self.overview_layout.addWidget(section_label)
            
            for cat in worst:
                cat_text = f"{cat['category']}: {cat['avg_score']}/10 avg ({cat['tasks_count']} tasks)"
                cat_label = QLabel(f"• {cat_text}")
                cat_label.setStyleSheet("color: #FFA500; font-size: 14px; margin-left: 20px;")
                self.overview_layout.addWidget(cat_label)
        
        self.overview_layout.addStretch()
    
    # ===== TAB 2: CATEGORIES =====
    
    def setup_categories_tab(self):
        """
        Vytvoří Categories tab
        """
        layout = QVBoxLayout()
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.categories_content = QWidget()
        self.categories_layout = QVBoxLayout()
        
        self.refresh_categories()
        
        self.categories_content.setLayout(self.categories_layout)
        scroll.setWidget(self.categories_content)
        
        layout.addWidget(scroll)
        self.categories_tab.setLayout(layout)
    
    def refresh_categories(self):
        """
        Refresh Categories tab obsah
        """
        # Vyčisti layout
        while self.categories_layout.count():
            child = self.categories_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Získej data
        categories = self.stats.get_category_stats(self.current_period)
        
        if not categories:
            no_data = QLabel("No data for this period")
            no_data.setStyleSheet("color: gray; font-size: 14px;")
            no_data.setAlignment(Qt.AlignCenter)
            self.categories_layout.addWidget(no_data)
            return
        
        # Pro každou kategorii vytvoř panel
        for cat in categories:
            panel = self.create_category_panel(cat)
            self.categories_layout.addWidget(panel)
        
        self.categories_layout.addStretch()
    
    def create_category_panel(self, cat):
        """
        Vytvoří panel pro jednu kategorii
        """
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: black;
                border: 1px solid white;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Header: kategorie + goal target
        header_layout = QHBoxLayout()
        
        cat_name = QLabel(cat['category'])
        cat_name.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        header_layout.addWidget(cat_name)
        
        header_layout.addStretch()
        
        if cat['goal_target']:
            goal_label = QLabel(f"Goal: {cat['goal_target']}/10")
            goal_label.setStyleSheet("font-size: 14px; color: lightgray;")
            header_layout.addWidget(goal_label)
        
        layout.addLayout(header_layout)
        
        # Progress bar + score
        progress_layout = QHBoxLayout()
        
        progress_bar = QProgressBar()
        progress_bar.setMaximum(10)

        #progress_bar.setValue(int(cat['avg_score']))

        avg_score = cat['avg_score'] if not (isinstance(cat['avg_score'], float) and math.isnan(cat['avg_score'])) else 0.0
        progress_bar.setValue(int(avg_score))
        
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(25)
        
        # Barva podle výkonu
        if cat['goal_target']:
            if cat['avg_score'] >= cat['goal_target']:
                color = "#00FF00"  # Zelená - splněno
            elif cat['avg_score'] >= cat['goal_target'] * 0.8:
                color = "#FFA500"  # Oranžová - blízko
            else:
                color = "#FF0000"  # Červená - nesplněno
        else:
            if cat['avg_score'] >= 7:
                color = "#00FF00"
            elif cat['avg_score'] >= 5:
                color = "#FFA500"
            else:
                color = "#FF0000"
        
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid white;
                background-color: black;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
        progress_layout.addWidget(progress_bar)
        
        score_label = QLabel(f"{cat['avg_score']}/10")
        score_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        progress_layout.addWidget(score_label)
        
        # Trend
        if cat['trend'] > 0:
            trend_label = QLabel(f"↗️ +{cat['trend']}")
            trend_label.setStyleSheet("color: #00FF00; font-size: 14px;")
        elif cat['trend'] < 0:
            trend_label = QLabel(f"↘️ {cat['trend']}")
            trend_label.setStyleSheet("color: #FF0000; font-size: 14px;")
        else:
            trend_label = QLabel("→ 0.0")
            trend_label.setStyleSheet("color: lightgray; font-size: 14px;")
        
        progress_layout.addWidget(trend_label)
        
        layout.addLayout(progress_layout)
        
        # Details
        details = f"Tasks: {cat['tasks_count']} | Hours: {cat['hours']}h | {cat['review_rate']}% reviewed"
        details_label = QLabel(details)
        details_label.setStyleSheet("color: lightgray; font-size: 12px; margin-top: 5px;")
        layout.addWidget(details_label)
        
        panel.setLayout(layout)
        
        return panel
    
    # ===== TAB 3: TRENDS =====
    
    def setup_trends_tab(self):
        """
        Vytvoří Trends tab
        """
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout()
        
        # ===== SCORE TREND =====
        score_label = QLabel("📈 SCORE OVER TIME (per week)")
        score_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 20px;")
        content_layout.addWidget(score_label)
        
        score_chart = self.create_score_chart()
        content_layout.addWidget(score_chart)
        
        # ===== HOURS TREND =====
        hours_label = QLabel("⏰ HOURS PER WEEK")
        hours_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 20px;")
        content_layout.addWidget(hours_label)
        
        hours_chart = self.create_hours_chart()
        content_layout.addWidget(hours_chart)
        
        content_layout.addStretch()
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        
        layout.addWidget(scroll)
        self.trends_tab.setLayout(layout)
    
    def create_score_chart(self):
        """
        Vytvoří ASCII chart pro score trend
        """
        data = self.stats.get_score_trend_per_week()
        
        if not data:
            label = QLabel("No data available")
            label.setStyleSheet("color: gray; font-size: 14px;")
            return label
        
        # ASCII chart
        chart_text = self.render_line_chart(data, max_val=10)
        
        chart_label = QLabel(chart_text)
        chart_label.setStyleSheet("color: white; font-family: monospace; font-size: 12px;")
        
        return chart_label
    
    def create_hours_chart(self):
        """
        Vytvoří ASCII bar chart pro hours
        """
        data = self.stats.get_hours_per_week()
        
        if not data:
            label = QLabel("No data available")
            label.setStyleSheet("color: gray; font-size: 14px;")
            return label
        
        # ASCII bar chart
        chart_text = self.render_bar_chart(data)
        
        chart_label = QLabel(chart_text)
        chart_label.setStyleSheet("color: white; font-family: monospace; font-size: 12px;")
        
        return chart_label
    
    def render_line_chart(self, data, max_val=10):
        """
        Renderuje ASCII line chart
        """
        if not data:
            return "No data"
        
        lines = []
        
        # Header
        lines.append(f"10 │")
        lines.append(f" 8 │")
        lines.append(f" 6 │")
        lines.append(f" 4 │")
        lines.append(f" 2 │")
        lines.append(f" 0 └" + "─" * 60)
        lines.append(f"    W1  W2  W3  W4  W5  W6  W7  W8  W9 W10 W11 W12")
        
        # Data points
        data_str = "Data: " + " | ".join([f"W{w}: {score}" for w, score in data])
        lines.append(data_str)
        
        return "\n".join(lines)
    
    def render_bar_chart(self, data):
        """
        Renderuje ASCII bar chart
        """
        if not data:
            return "No data"
        
        max_hours = max(h for _, h in data) if data else 1
        
        lines = []
        
        for week, hours in data:
            bar_length = int((hours / max_hours) * 40) if max_hours > 0 else 0
            bar = "█" * bar_length
            lines.append(f"W{week:2d} │{bar} {hours}h")
        
        return "\n".join(lines)
    
    # ===== TAB 4: GOALS =====
    
    def setup_goals_tab(self):
        """
        Vytvoří Goals tab
        """
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        self.goals_layout = QVBoxLayout()
        
        self.refresh_goals()
        
        content.setLayout(self.goals_layout)
        scroll.setWidget(content)
        
        layout.addWidget(scroll)
        self.goals_tab.setLayout(layout)
    
    def refresh_goals(self):
        """
        Refresh Goals tab obsah
        """
        # Vyčisti layout
        while self.goals_layout.count():
            child = self.goals_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Získej data
        goals = self.stats.get_goals_progress()
        
        if not goals:
            no_goals = QLabel("No goals for current cycle")
            no_goals.setStyleSheet("color: gray; font-size: 14px;")
            no_goals.setAlignment(Qt.AlignCenter)
            self.goals_layout.addWidget(no_goals)
            return
        
        # Pro každý goal vytvoř panel
        for goal in goals:
            panel = self.create_goal_panel(goal)
            self.goals_layout.addWidget(panel)
        
        self.goals_layout.addStretch()
    
    def create_goal_panel(self, goal):
        """
        Vytvoří panel pro jeden goal
        """
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: black;
                border: 1px solid white;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Header: status icon + goal name
        header_layout = QHBoxLayout()
        
        if goal['status'] == 'exceeding':
            icon = "✅"
            color = "#00FF00"
        elif goal['status'] == 'on_track':
            icon = "🎯"
            color = "#FFA500"
        else:
            icon = "⚠️"
            color = "#FF0000"
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        goal_name = QLabel(goal['goal_name'])
        goal_name.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        header_layout.addWidget(goal_name)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Targets
        target_text = f"Target: {goal['target_hours']}h @ {goal['target_score']} avg score"
        target_label = QLabel(target_text)
        target_label.setStyleSheet("color: lightgray; font-size: 14px;")
        layout.addWidget(target_label)
        
        # Actual
        actual_text = f"Actual: {goal['actual_hours']}h @ {goal['actual_score']} avg score"
        actual_label = QLabel(actual_text)
        actual_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(actual_label)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(goal['progress_percent']))
        progress_bar.setFormat(f"{goal['progress_percent']}%")
        progress_bar.setFixedHeight(25)
        
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid white;
                background-color: black;
                color: white;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
        progress_layout.addWidget(progress_bar)
        
        layout.addLayout(progress_layout)
        
        # Status
        if goal['status'] == 'exceeding':
            status_text = "Status: EXCEEDING! 🎉"
        elif goal['status'] == 'on_track':
            status_text = "Status: ON TRACK ✅"
        else:
            status_text = "Status: BEHIND SCHEDULE ⚠️"
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold; margin-top: 5px;")
        layout.addWidget(status_label)
        
        panel.setLayout(layout)
        
        return panel