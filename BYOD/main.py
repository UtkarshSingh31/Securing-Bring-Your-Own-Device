import time
from logging_handler import log_visit


URL_LIST = [
    (101,"https://www.github.com", 400,"gchahar0806gmail.com"), 
    (102,"https://www.instagram.com", 600,"try.nitinchahar@gmail.com"), 
    (102,"https://www.youtube.com/wwe",350,"try.nitinchahar@gmail.com"),
    (101,"https://www.youtube.com/freecodecamp",800,"gchahar0806gmail.com"),
    (102,"https://www.youtube.com/@bbkivines",1000,"try.nitinchahar@gmail.com"),
    (101,"https://www.leetcode.com",350,"gchahar0806gmail.com"),
    (102,"https://ums.lpu.in",200,"try.nitinchahar@gmail.com")
]

if __name__ == "__main__":
    print("Tracking URL activity...\n")
    
    for user_id, url, time_spent,email in URL_LIST:
        log_visit(user_id,url, time_spent,email)
        time.sleep(2)  # Simulate delay between visits

    print("\n All URLs processed. Check 'student_activity.csv' for logs!")

