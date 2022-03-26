from datetime import datetime
import ast, os


days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Sunday', 'Saturday']

months = {"September": "9", "October": "10", "November": "11", "December": "12", "January": "1", "February": "2", "March": "3", "April": "4", "May": "5"}

int_months = {9: "September", 10: "October", 11: "November", 12: "December", 1: "January", 2: "February", 3: "March", 4: "April", 5: "May"}

days_per_month = {"September": 30, "October": 31, "November": 30, "December": 31, "January": 31, "February": 28, "March": 31, "April": 30, "May": 31}

days_week = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Sunday", 7: "Saturday"}


def get_date() -> str:
    return str(".".join(str(datetime.today().date()).split("-")[::-1]))


def get_beauty_date(date: str) -> str:
    day = int(date.split(".")[0])
    month = int(date.split(".")[1])
    year = int(date.split(".")[2])
    if day < 10:
        day = f"0{day}"
    if month < 10:
        month = f"0{month}"
    return f"{day}.{month}.{year}"


def get_date_from_now(plus: int) -> str:
    output = str(".".join(str(datetime.today().date()).split("-")[::-1]))
    new_day = int(output.split('.')[0]) + plus
    month = int(output.split('.')[1])
    new_year = int(output.split('.')[2])
    if new_day > days_per_month[int_months[month]]:
        overtaking = new_day - days_per_month[int_months[month]] - 1
        new_day = 1 + overtaking
        if month == 12:
            month = 1
        else:
            month += 1
    if month == 1:
        new_year = 2022
    if new_day < 10:
        new_day = f"0{new_day}"
    else:
        new_day = str(new_day)
    if month < 10:
        month = f"0{month}"
    else:
        month = str(month)
    output_new = f"{new_day}.{month}.{new_year}"
    return output_new


def detect_day(day) -> str:
    if day in days["rus"].keys():
        return days["rus"][day]
    elif day in days["eng"].keys():
        return day


def get_int_of_week() -> int:
    return datetime.now().weekday()


def get_year() -> str:
    return str(datetime.now().year)


def get_good_date(date: str):
    date_list = date.split(".")
    if len(date_list[2]) == 4:
        date_list[2] = date_list[2][2::]
    return f"{int(date_list[0])}.{int(date_list[1])}.{int(date_list[2])}"


def get_int_of_month() -> int:
    return int(datetime.now().month)


def get_current_day() -> int:
    return int(datetime.now().day)


def read_database():
    if not os.path.exists("database/database.db"):
        return None
    with open("database/database.db", "r") as f:
        output = ast.literal_eval(f.read())
        f.close()
    return output


def save_database(database):
    if not os.path.exists("database"):
        os.mkdir("database")
    with open("database/database.db", "w") as f:
        f.write(str(database))
        f.close()