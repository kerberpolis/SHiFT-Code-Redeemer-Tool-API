"""File containing common functions"""
from datetime import datetime

import pytz
from cryptography.fernet import Fernet


#  todo: parse datetime expiration date in tweet. expiration is not always present. Most seem to be in UTC so far.
def convert_date(str_date: str):
    if str_date:
        tzone_dic = {
            'PST': '-0800', 'PDT': '-0700', 'MST': '-0700',
            'MDT': '-0600', 'CST': '-0600', 'CDT': '-0500',
            'EST': '-0500', 'EDT': '-0400',
        }

        # datetime does not recognise PST, CST, EST etc. for dt formatting using %Z,
        # instead use dict to replace the tz with UTC offset, %z.
        if any(tzone in str_date for tzone in tzone_dic.keys()):
            for key in tzone_dic.keys():
                if key in str_date:
                    str_date = str_date.replace(key, tzone_dic[key])

        # 11 Jan 14:00 Sunday, 11 Jan 13:00, 11 Jan, 11 JUNE, 2 JUN 07:59 UTC, 20 APR 23:59 -0500
        # 26 May 2022 17:30:00 -0400
        date_patterns = ['%d %b %Y %H:%M %Z', '%d %b %H:%M %A', '%d %b %H:%M', '%d %b', '%d %B',
                         '%d %b %H:%M %Z', '%d %b %H:%M %z', '%d %b %H:%M %Z', '%d %b %Y %H:%M:%S %z']

        for pattern in date_patterns:
            try:
                dt = datetime.strptime(str_date, pattern)
                if dt.tzinfo:
                    # convert dt to utc
                    dt = datetime.strptime(dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                                           "%Y-%m-%d %H:%M:%S")
                # It's {CURRENT YEAR}! replace dt year (1900) with current year
                dt = dt.replace(year=datetime.now().year)
                return dt
            except ValueError:
                pass
            except pytz.UnknownTimeZoneError:
                print('Unknown timezone')
                pass

    return "Unknown"


def encrypt(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)
