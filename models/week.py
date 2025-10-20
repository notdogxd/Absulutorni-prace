# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
from datetime import datetime 
from main import nProgram

# Fix Windows console encoding for Czech characters
sys.stdout.reconfigure(encoding='utf-8')

class Week(nProgram):
    tasks = []
    def __init__(self, week_number, start_date, end_date, time_blocks, tasks):
        day_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        timer = 10000 #hodin
        self.week_number = week_number
        self.start_date = start_date
        self.end_date = end_date
        self.time_blocks = time_blocks
        self.tasks = tasks


        def rate(self, score):
            if self.completed:
                if self.rating is None:
                    self.rating = score
                    print(f"⭐ Hodnocení: {score}/10")
                else:
                    print("Už máš zapsáno")

    # budeme pridavat tasky, ale budeme pouzivat tridy

        def add_task(self, task):
            tasks.append(task)
            return tasks
        
        def remove_task(self, task):
            tasks.remove(task)
            return tasks

        def get_tasks(self, tasks, week_number):
            if week_number == True: # misto true task number
                return tasks # that have a same week_number
        def get_completed_tasks(self):
            pass
        def get_pending_tasks(self):
            pass
        def mark_week_complete(self):
            pass
        def rate_week(self):
            pass
        def calculate_week_stats(self):
            pass
        def filter_tasks_by_day(day_name):
            self
        def get_time_blocks(self):
            pass
        def get_weekly_summary(self):
            pass
        def get_weekly_summary(self):
            pass
        def get_days_remaining(self):
            pass
        def get_week_progress(self):
            pass
        def save_to_db(self):
            pass
        def load_from_db(week_number):
            pass
        def update_in_db(self):
            pass
