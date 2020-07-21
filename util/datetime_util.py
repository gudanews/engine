from datetime import datetime, timedelta
from datetime import date
import re

TODAY = date.today()
NOW = datetime.now()
ANY_MONTHS_3L = "JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"
ANY_MONTHS = "JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER"
ANY_TIMEZONE = "PST|PDT|EST|EDT|UTC"
DATETIME_REGEX = dict(
    hh_mm_12= r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<period>AM|PM)$',  # 08:33AM
    hh_mm_24 = r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})$',  # 20:33
    hh_mm_12_zone=r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<period>AM|PM) (?P<zone>%s)$' % ANY_TIMEZONE,  # 08:33AM EDT
    hh_mm_24_zone=r'^(?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<zone>PST|EST)$',  # 20:33 PST
    month_day_year=r'^(?P<month>%s) (?P<day>\d{1,2}) (?P<year>\d{2,4})$' % ANY_MONTHS_3L,  # JUL 7 2020
    mon_day_year = r'^(?P<month>%s) (?P<day>\d{1,2}) (?P<year>\d{2,4})$' % ANY_MONTHS  # JUL 7 2020
)
def _convert_month(month):
    MONTH_3L = dict(JAN=1,FEB=2,MAR=3,APR=4,MAY=5,JUN=6,JUL=7,AUG=8,SEP=9,OCT=10,NOV=11,DEC=12)
    MONTH = dict(JANUARY=1,FEBURARY=2,MARCH=3,APRIL=4,MAY=5,JUNE=6,JULY=7,AUGUST=8,SEPTEMBER=9,OCTOBER=10,NOVEMBER=11,DECEMBER=12)
    if not month:
        return None
    if month.upper() in MONTH.keys():
        return MONTH[month.upper()]
    if month.upper() in MONTH_3L.keys():
        return MONTH_3L[month.upper()]
    return None

def _adjust_timezone(zone):
    if zone and zone.upper() in ("EST", "EDT"):
        return -3
    return 0

def str2datetime(p_time):
    for _,pattern in DATETIME_REGEX.items():
        m = re.match(pattern, p_time, re.IGNORECASE)
        if m:
            adj_hour = 0 # Adjust time zone and period
            d_time = m.groupdict()
            for key in ("year", "month", "day", "hour", "minute"):
                if key in d_time:
                    if d_time[key].isdigit():
                        d_time[key] = int(d_time[key])
                else:
                    exec("d_time['" + key + "'] = NOW." + key)
            if isinstance(d_time["month"], str):
                d_time["month"] = _convert_month(d_time["month"])
            if "period" in d_time:
                if d_time["period"].upper() == "PM":
                    adj_hour += 12
                del d_time["period"]
            if "zone" in d_time:
                adj_hour += _adjust_timezone(d_time["zone"])
                del d_time["zone"]
            r_time = datetime(**d_time) + timedelta(hours=adj_hour)
            return r_time


import unittest
class TestDateTime(unittest.TestCase):
    def test_string_to_datetime(self):
        result = str2datetime("03:30 EST")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,0,30)))
        result = str2datetime("03:30PM PST")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,15,30)))
        result = str2datetime("03:30")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,3,30)))
        result = str2datetime("03:30PM")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,15,30)))
        result = str2datetime("Jul 03 2020")
        self.assertEqual(str(result), str(datetime(2020,7,3,NOW.hour,NOW.minute)))
        result = str2datetime("August 03 2020")
        self.assertEqual(str(result), str(datetime(2020,8,3,NOW.hour,NOW.minute)))

if __name__ == '__main__':
    unittest.main()