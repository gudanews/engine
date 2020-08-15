from datetime import datetime, timedelta
from datetime import date
import re
import logging
import unittest
from util.common import LoggedTestCase
import time


logger = logging.getLogger("Util.Datetime")

TODAY = date.today()
NOW = datetime.now()
ANY_MONTHS_3L = "JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"
ANY_MONTHS = "JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER"
ANY_WEEK_DAYS_2L = "MO|TU|WE|TH|FR|SA|SU"
ANY_WEEK_DAYS_3L = "MON|TUE|WED|THU|FRI|SAT|SUN"
ANY_WEEK_DAYS = "MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY"
ANY_DAYS = "DAY|DAYS|D|DS"
ANY_HOURS = "HOUR|HOURS|HR|HRS|H|HS"
ANY_MINUTES = "MIN|MINS|M|MS"
ANY_TIMEZONE = "UTC|GMT|Z|EDT|EST|ET|CDT|CST|CT|MDT|MST|MT|PDT|PST|PT|AKDT|AKST|HST"
DATETIME_REGEX = dict(
    hh_mm_12= r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<period>AM|PM)$',  # 08:33AM
    hh_mm_24 = r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})$',  # 20:33
    hh_mm_12_zone=r'^(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<period>AM|PM) (?P<zone>%s)$' % ANY_TIMEZONE,  # 08:33AM EDT
    hh_mm_24_zone=r'^(?P<hour>\d{1,2}):(?P<minute>\d{2}) (?P<zone>%s)$' % ANY_TIMEZONE,  # 20:33 PST
    month_day_year=r'^(?P<month>%s)(\.|)(\s{0,1})(?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4})$' % ANY_MONTHS_3L,  # JUL 7 2020
    mon_day_year = r'^(?P<month>%s)(\.|)(\s{0,1})(?P<day>\d{1,2})(\,{0,1}) (?P<year>\d{2,4})$' % ANY_MONTHS,  # JUL 7 2020
    month_day=r'^(?P<month>%s)(\.{0,1})(\s|)(?P<day>\d{1,2})(\,{0,1})$' % ANY_MONTHS_3L,  # JUL 7
    mon_day = r'^(?P<month>%s)(\.{0,1})(\s|)(?P<day>\d{1,2})(\,{0,1})$' % ANY_MONTHS,  # JUL 7
    day_ago = r'^(?P<ago_day>\d{1,2})(\s|)(%s) (?P<ago>AGO)$' % ANY_DAYS,  # 2 days ago
    hour_min_ago = r'^(?P<ago_hour>\d{1,2})(\s|)(%s)(?P<ago_minute>\d{1,2})(\s|)(%s) (?P<ago>AGO)$' % (ANY_HOURS, ANY_MINUTES),  # 2h30m ago
    hour_ago = r'^(?P<ago_hour>\d{1,2})(\s|)(%s) (?P<ago>AGO)$' % ANY_HOURS,  # 10 hours ago
    min_ago = r'^(?P<ago_minute>\d{1,2})(\s|)(%s) (?P<ago>AGO)$' % ANY_MINUTES,  # 4mins ago
    year_month_day_hh_mm_ss = r'^(?P<year>\d{2,4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})(T| )(?P<hour>\d{1,2}):(?P<minute>\d{2}):(?P<second>\d{2})$', # 2020-07-26T16:23:55
    year_month_day_hh_mm_ss_zone = r'^(?P<year>\d{2,4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})(T| )(?P<hour>\d{1,2}):(?P<minute>\d{2}):(?P<second>\d{2})(\s|)(?P<zone>\S+)$'  # 2020-07-26T16:23:55-04:00
)
LOCAL_TIME_ZONE = time.localtime().tm_zone
IS_DST = time.localtime().tm_isdst # 1 for DST, 0 for No
TIME_ZONE = dict(UTC=0, GMT=0, Z=0, EDT=-4, EST=-5, ET=-5+IS_DST, CDT=-5, CST=-6, CT=-6+IS_DST,
                 MDT=-6, MST=-7, MT=-7+IS_DST, PDT=-7, PST=-8, PT=-8+IS_DST, AKDT=-8, AKST=-9, HST=-10)

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

def _adjust_timezone(zone):
    adjust = 0
    if zone:
        m = re.match(r'^(-|\+)(\d+)', zone, re.IGNORECASE)
        if m:
            tz = int(m.group())
        else:
            if zone.upper() not in TIME_ZONE.keys():
                logger.warning("Cannot find timezone [%s]" % zone)
                return 0
            tz = TIME_ZONE[zone.upper()]
        adjust = TIME_ZONE[LOCAL_TIME_ZONE] - tz
    return adjust

def str2datetime(p_time):
    if p_time: # Return current time if p_time is None
        for _, pattern in DATETIME_REGEX.items():
            if re.match(pattern, p_time, re.IGNORECASE):
                return get_datetime_use_pattern(pattern, p_time)
    logger.warning("Cannot find the expected time format [%s]" % p_time)
    return NOW

def get_datetime_use_pattern(pattern, p_time):
    m = re.match(pattern, p_time, re.IGNORECASE)
    if m:
        adj_day = 0  # Adjust days
        adj_hour = 0  # Adjust hours due to time zone and period and ago
        adj_minute = 0  # Adjust minutes
        ic_time = m.groupdict()
        if "zone" in ic_time:  # Adjust timezone to current local time
            adj_hour = _adjust_timezone(ic_time["zone"])
            if not "day" in ic_time:
                if (NOW.hour - adj_hour - 24) * 60 + NOW.minute > int(ic_time["hour"]) * 60 + int(
                        ic_time["minute"]):  # 02:34AM EST at morning
                    adj_hour += 24
                elif (NOW.hour - adj_hour + 24) * 60 + NOW.minute < int(ic_time["hour"]) * 60 + int(
                        ic_time["minute"]):  # 23:34PM HST at late night
                    adj_hour -= 24
            del ic_time["zone"]
        for key in ("year", "month", "day", "hour", "minute", "second"):
            if key in ic_time:
                if ic_time[key].isdigit():
                    ic_time[key] = int(ic_time[key])
            else:
                if key in ("hour", "minute", "second") and not "ago" in ic_time:  # if time not specified set to 00:00
                    ic_time[key] = 0
                else:
                    exec("ic_time['" + key + "'] = NOW." + key)

        if isinstance(ic_time["month"], str):  # e.g. Convert ic_time["month"] = July to 7
            ic_time["month"] = _convert_month_to_number(ic_time["month"])
        if "period" in ic_time:  # Adjust PM to 24 hour format
            if ic_time["period"].upper() == "PM" and ic_time["hour"] != 12:  # 3PM -> 15, but 12PM -> 12
                adj_hour += 12
            del ic_time["period"]
        if "ago" in ic_time:  # Adjust time deltas
            if "ago_day" in ic_time:
                adj_day -= int(ic_time.pop("ago_day"))
            if "ago_hour" in ic_time:
                adj_hour -= int(ic_time.pop("ago_hour"))
            if "ago_minute" in ic_time:
                adj_minute -= int(ic_time.pop("ago_minute"))
            del ic_time["ago"]
        r_time = datetime(**ic_time) + timedelta(days=adj_day, hours=adj_hour, minutes=adj_minute)
        logger.debug("Convert [%s] to standardized datetime [%s]" % (p_time, r_time))
        return r_time
    return None


class TestDateTime(LoggedTestCase):

    def test_string_to_datetime0(self):
        result = str2datetime("10 days ago")
        self.assertEqual(str(result), str(
            datetime(TODAY.year, TODAY.month, TODAY.day, NOW.hour, NOW.minute, NOW.second) - timedelta(days=10)))

    def test_string_to_datetime1(self):
        result = str2datetime("2h30m ago")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,NOW.hour,NOW.minute,NOW.second) - timedelta(hours=2, minutes=30)))

    def test_string_to_datetime2(self):
        result = str2datetime("10 hours ago")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,NOW.hour,NOW.minute,NOW.second) - timedelta(hours=10)))

    def test_string_to_datetime3(self):
        result = str2datetime("4min ago")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,NOW.hour,NOW.minute,NOW.second) - timedelta(minutes=4)))

    def test_string_to_datetime4(self):
        result = str2datetime("01:30 EDT")
        if NOW.hour * 60 + NOW.minute > 21 * 60 + 30 + IS_DST * 60:
            self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,21,30,0) + timedelta(hours=IS_DST)))
        else:
            self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,21,30,0) + timedelta(hours=IS_DST) - timedelta(days=1)))

    def test_string_to_datetime5(self):
        result = str2datetime("03:30 EST")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,0,30,0) + timedelta(hours=IS_DST)))

    def test_string_to_datetime6(self):
        result = str2datetime("03:30PM PST")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,15,30,0) + timedelta(hours=IS_DST)))

    def test_string_to_datetime7(self):
        result = str2datetime("03:30")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,3,30,0)))

    def test_string_to_datetime8(self):
        result = str2datetime("03:30PM")
        self.assertEqual(str(result), str(datetime(TODAY.year,TODAY.month,TODAY.day,15,30,0)))

    def test_string_to_datetime9(self):
        result = str2datetime("Jul 03 2020")
        self.assertEqual(str(result), str(datetime(2020,7,3,0,0,0)))

    def test_string_to_datetime10(self):
        result = str2datetime("Jul 03, 2020")
        self.assertEqual(str(result), str(datetime(2020,7,3,0,0,0)))

    def test_string_to_datetime11(self):
        result = str2datetime("August 03 2020")
        self.assertEqual(str(result), str(datetime(2020,8,3,0,0,0)))

    def test_string_to_datetime12(self):
        result = str2datetime("August 03, 2020")
        self.assertEqual(str(result), str(datetime(2020,8,3,0,0,0)))

    def test_string_to_datetime13(self):
        result = str2datetime(None)
        self.assertEqual(str(result), str(NOW))

    def test_string_to_datetime14(self):
        result = str2datetime("2020-07-26T16:23:55-04:00")
        self.assertEqual(str(result), str(datetime(2020,7,26,12,23,55) + timedelta(hours=IS_DST)))

    def test_string_to_datetime15(self):
        result = str2datetime("2020-07-26T02:23:55-04:00")
        self.assertEqual(str(result), str(datetime(2020,7,25,22,23,55) + timedelta(hours=IS_DST)))

    def test_string_to_datetime16(self):
        result = str2datetime("2020-07-26T02:23:55EDT")
        self.assertEqual(str(result), str(datetime(2020,7,25,22,23,55) + timedelta(hours=IS_DST)))

    def test_string_to_datetime16(self):
        result = str2datetime("2020-07-29T04:41:55Z")
        self.assertEqual(str(result), str(datetime(2020,7,28,20,41,55) + timedelta(hours=IS_DST)))

if __name__ == '__main__':
    unittest.main()