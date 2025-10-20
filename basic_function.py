# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
from datetime import datetime 

# Fix Windows console encoding for Czech characters
sys.stdout.reconfigure(encoding='utf-8')

# numbers = [1, 2, 3 , 4 ,5]
# def calculate_average(numbers):
#     total = sum(numbers)
#     print( total / len(numbers))
# calculate_average(numbers)

tasks = [
    {"title": "Cvičení", "completed": True, "week_number": 1, "min_rating": 4},
    {"title": "Učení", "completed": False,"week_number": 2, "min_rating": 7},
    {"title": "Nákup", "completed": True,"week_number": 3, "min_rating": 9},
    {"title": "Programování", "completed": False, "week_number": 4, "min_rating": 2}
]

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

#first classes, target_date abychom vedeli kdy mame vytovrit task   
class Task:
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

# Úkol PRO dneska (automaticky)
task1 = Task("Email", week_number=1)
task1.mark_complete()
task1.rate(8)
task1.rate(10)  
# target_date = dneska
print(task1)
# Úkol PRO zítra (explicitně zadáš)
task2 = Task("Meeting", week_number=1, target_date="2024-10-15")
# target_date = zítra
print(task2)