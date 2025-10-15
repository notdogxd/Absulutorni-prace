import sqlite3

# numbers = [1, 2, 3 , 4 ,5]
# def calculate_average(numbers):
#     total = sum(numbers)
#     print( total / len(numbers))
# calculate_average(numbers)

tasks = [
    {"title": "Cvičení", "completed": True, "week_number": 1},
    {"title": "Učení", "completed": False,"week_number": 2},
    {"title": "Nákup", "completed": True,"week_number": 3},
    {"title": "Programování", "completed": False, "week_number": 4}
]
print(tasks["title": "Cvičení"])

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
def filter_by_week(week):
    return