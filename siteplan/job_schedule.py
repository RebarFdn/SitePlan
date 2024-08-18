import schedule
import time


def job():
    print(time.time(), "Im Still Working...")

def job2():
    print(time.time(), "Im Working Breakfast..")

def job3():
    print(time.time(), "Im Still Working on Lunch...")


# Run job every 3 second/minute/hour/day/week,
# Starting 3 second/minute/hour/day/week from now
schedule.every(5).seconds.do(job)
schedule.every(1).minutes.do(job2)
schedule.every(1).hours.do(job3)


def runner():
    while True:
        schedule.run_pending()
        time.sleep(1)