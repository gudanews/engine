from datetime import datetime, timedelta
from datetime import date
import re
import logging
import unittest
from util.common import LoggedTestCase


logger = logging.getLogger("Util.Datetime")

TODAY = date.today()
NOW = datetime.now()
ANY_MONTHS_3L = "JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"
ANY_MONTHS = "JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER"
ANY_HOURS = "HOUR|HOURS|HR|HRS|H|HS"
ANY_MINUTES = "MIN|MINS|M|MS"
ANY_TIMEZONE = "PST|PDT|EST|EDT|UTC"
DATETIME_REGEX = dict(
    hh_mm_12= r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<period>AM|PM)$',  # 08:33AM
    hh_mm_24 = r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})$',  # 20:33
    hh_mm_12_zone=r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<period>AM|PM) (?P<zone>%s)$' % ANY_TIMEZONE,  # 08:33AM EDT
    hh_mm_24_zone=r'^(?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<zone>PST|EST)$',  # 20:33 PST
    month_day_year=r'^(?P<month>%s) (?P<day>\d{1,2}) (?P<year>\d{2,4})$' % ANY_MONTHS_3L,  # JUL 7 2020
    mon_day_year = r'^(?P<month>%s) (?P<day>\d{1,2}) (?P<year>\d{2,4})$' % ANY_MONTHS,  # JUL 7 2020
    min_ago = r'^(?P<ago_minute>\d{1,2})(\s{0,1})(%s) (?P<ago>AGO)$' % ANY_MINUTES,  # 4mins ago
    hour_ago = r'^(?P<ago_hour>\d{1,2})(\s{0,1})(%s) (?P<ago>AGO)$' % ANY_HOURS,  # 10 hours ago
    hour_min_ago = r'^(?P<ago_hour>\d{1,2})(\s{0,1})(%s)(?P<ago_minute>\d{1,2})(\s{0,1})(%s) (?P<ago>AGO)$' % (ANY_HOURS, ANY_MINUTES)  # 2h30m ago
)
def _convert_month_to_number(month):
    MONTH_3L = dict(JAN=1,FEB=2,MAR=3,APR=4,MAY=5,JUN=6,JUL=7,AUG=8,SEP=9,OCT=10,NOV=11,DEC=12)
    MONTH = dict(JANUARY=1,FEBURARY=2,MARCH=3,APRIL=4,MAY=5,JUNE=6,JULY=7,AUGUST=8,SEPTEMBER=9,OCTOBER=10,NOVEMBER=11,DECEMBER=12)
    if not month:
        return None
    if month.upper() in MONTH.keys():
        return MONTH[month.upper()]
    if month.upper() in MONTH_3L.keys():
        return MONTH_3L[month.upper()]
    return None

def _adjust_timezone(hour, zone):
    adjust = 0
    if zone and zone.upper() in ("EST", "EDT"):
        adjust -= 3
        if hour < 3:
            adjust += 24
    return adjust

def str2datetime(p_time):
    for _,pattern in DATETIME_REGEX.items():
        m = re.match(pattern, p_time, re.IGNORECASE)
        if m:
            adj_hour = 0 # Adjust hours due to time zone and period and ago
            adj_minute = 0 # Adjust minutes
            d_time = m.groupdict()
            for key in ("year", "month", "day", "hour", "minute"):
                if key in d_time:
                    if d_time[key].isdigit():
                        d_time[key] = int(d_time[key])
                else:
                    exec("d_time['" + key + "'] = NOW." + key)
            if isinstance(d_time["month"], str): # e.g. Convert d_time["month"] = July to 7
                d_time["month"] = _convert_month_to_number(d_time["month"])
            if "period" in d_time: # Adjust PM to 24 hour format
                if d_time["period"].upper() == "PM" and d_time["hour"] != 12: # 3PM -> 15, but 12PM -> 12
                    adj_hour += 12
                del d_time["period"]
            if "zone" in d_time: # Adjust timezone to current local time
                adj_hour += _adjust_timezone(d_time["hour"], d_time["zone"])
                del d_time["zone"]
            if "ago" in d_time: # Adjust time deltas
                if "ago_hour" in d_time:
                    adj_hour -= int(d_time.pop("ago_hour"))
                if "ago_minute" in d_time:
                    adj_minute -= int(d_time.pop("ago_minute"))
                del d_time["ago"]
            r_time = datetime(**d_time) + timedelta(hours=adj_hour, minutes=adj_minute)
            logger.debug("Convert [%s] to standardized datetime [%s]" %
                         (p_time, r_time))
            return r_time


class TestDateTime(LoggedTestCase):

    def test_string_to_datetime(self):
        result = str2datetime("2h30m ago")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,NOW.hour,NOW.minute) - timedelta(hours=2, minutes=30)))
        result = str2datetime("10 hours ago")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,NOW.hour,NOW.minute) - timedelta(hours=10)))
        result = str2datetime("4min ago")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,NOW.hour,NOW.minute) - timedelta(minutes=4)))
        result = str2datetime("02:30 EST")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,23,30)))
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