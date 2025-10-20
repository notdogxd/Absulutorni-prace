# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
from datetime import datetime 
from main import nProgram

# Fix Windows console encoding for Czech characters
sys.stdout.reconfigure(encoding='utf-8')


#first classes, target_date abychom vedeli kdy mame vytovrit task   
class Task(nProgram):
    def __init__(self, title, week_number, description="", target_date=None):
        self.title = title
        self.week_number = week_number
        self.description = description
        self.created_at = datetime.now()
        self.completed = False
        self.rating = None

    #
        if target_date is None:
            self.target_date = self.created_at.date()
        else:
            self.target_date = target_date

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
        else:
            print("❌ Nejdřív musíš dokončit úkol!")

    def __str__(self):
        return f"Task: {self.title} (Week{self.week_number}) (created date {self.target_date})"


def filter_completed(tasks):
    completed_tasks = []

    for x in tasks:
        if x["completed"] == True:
        #if x["completed"]: same
            completed_tasks.append(x)
    
    return completed_tasks 


print(filter_completed(tasks))

def filter_incompleted(tasks):
    incompleted_tasks = []

    for x in tasks:

        if x["completed"] == False:
        #if not x["completed"]:
            incompleted_tasks.append(x)

    return incompleted_tasks
    
print(filter_incompleted(tasks))


#comprehension
def comprehension_completed(tasks):
    return [x for x in tasks if x["completed"]]

print(comprehension_completed(tasks))


#filter podle tyden
def filter_by_week(tasks, week_number):
     return [x for x in tasks if x["week_number"] == week_number]

print(filter_by_week(tasks, 2))

def filter_high_rated(tasks, min_rating):
    return [x for x in tasks if x["min_rating"] >= min_rating]

print(filter_high_rated(tasks, 5))
