# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
from datetime import datetime 

# Fix Windows console encoding for Czech characters
sys.stdout.reconfigure(encoding='utf-8')

class Time_block:
    def __init__(self, duration, week_number, description=""):
        self.duration = duration
        self.week_number = week_number
        self.description = description
        self.rating = None
        self.created_at = datetime.now()
        self.completed = False

        # funkce ktera vezme creted_at a prida o to duration
    def add(self):
        final_time = self.created_at + self.duration
        return final_time
    
    def mark_complete(self):
        self.completed = True
        print(f"✅ {self.title}")

    def rate(self, score):
        if self.completed:
            if self.rating is None:
                self.rating = score
                print(f"⭐ Hodnocení: {score}/10")
            else:
                print("Už máš zapsáno")
                
