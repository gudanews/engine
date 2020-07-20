from datetime import datetime
from datetime import date
def str2datetime(time):
    return _convert_month_day_year_to_datetime(time)
    #if time matches"":
    #case1: "18:03"
    #case2: "06:03PM"
    #case: "2020 July 18"
    #case4: "July 18"
def _get_day():
    day = ''
    for i in str(datetime.now()):
        if i == ' ':
            break
        else:
            day += i
    day+=' '
    return day
def convert_to_datetime(time):
    try:
        convert_EDT_to_datetime(time)
    except:
        _convert_month_day_year_to_datetime(time)
def check_if_time_valid(time):
    pass
def _convert_24hour_minute_to_datetime(time):
    day = _get_day()
    return datetime.strptime(day+time,"%Y-%m-%d %H:%M")
def _convert_12hour_minute_to_datetime(time):
    day = _get_day()
    return  datetime.strptime(day+time,"%Y-%m-%d %H:%M%p")
def _convert_month_day_year_to_datetime(time):
    return datetime.strptime(time, '%b %d %Y')
def _convert_year_month_day_to_datetime(time):
    return datetime.strptime(time,"%Y %B %d")

def convert_EDT_to_datetime(time):
    day = ''
    for i in str(datetime.now()):
        if i != ' ':
            day += i
        else:
            break
    hour = ''
    minute = ''
    op = False
    if "PM" in time:
        for i in time:
            if i == 'P':
                break
            if i == ':':
                op = True
            if op == False:
                hour += i
            if op == True:
                minute += i

        hour = int(hour)
        hour += 12
        hour = hour % 24
    elif "AM" in time:
        for i in time:
            if i == 'A':
                break
            if i == ':':
                op = True
            if op == False:
                hour += i
            if op == True:
                minute += i
    return datetime.strptime(day + ' ' + str(hour) + minute,'%Y-%m-%d %H:%M')

#print(datetime.strptime('8:29PM EDT','%H:%M%p EDT'))



import unittest
class TestDateTime(unittest.TestCase):
    def test_get_table_records(self):
        result = str2datetime("Jul 03 2020")
        self.assertEqual(str(result), str(datetime(2020, 7, 3)))

if __name__ == '__main__':
    unittest.main()