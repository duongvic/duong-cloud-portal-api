#
# Copyright (c) 2020 FTI-CAS
#

import datetime

from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta

from application import app

LOG = app.logger

"""Epoch datetime"""
EPOCH = datetime.datetime.utcfromtimestamp(0)


def utc_now(timespec=None):
    """
    Get current UTC time with timespec.
    :param timespec: can be one of 'seconds', 'minutes', 'hours',
            'days', 'months', 'years'
    :return:
    """
    now = datetime.datetime.utcnow()
    if timespec:
        if timespec == 'seconds':
            now = now.replace(microsecond=0)
        elif timespec == 'minutes':
            now = now.replace(second=0, microsecond=0)
        elif timespec == 'hours':
            now = now.replace(minute=0, second=0, microsecond=0)
        elif timespec == 'days':
            now = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif timespec == 'months':
            now = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif timespec == 'years':
            now = now.replace(month=1, day=0, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise TypeError('Invalid timespec: ' + str(timespec))
    return now


def utc_now_as_sec():
    """
    Get UTC time as number of seconds since EPOCH.
    :return:
    """
    return (datetime.datetime.utcnow() - EPOCH).total_seconds()


def utc_now_as_ms():
    """
    Get UTC time as number of milliseconds since EPOCH.
    :return:
    """
    return (datetime.datetime.utcnow() - EPOCH).total_seconds() * 1000


def utc_now_as_date():
    """
    Get UTC time as a date only without time fields.
    :return:
    """
    return datetime.datetime.utcnow().date()


def utc_from_timestamp(timestamp):
    """
    Calculate UTC time from timestamp as seconds.
    Restricted to years in 1970 through 2038.
    :param timestamp: floating point number of seconds
    :return:
    """
    return datetime.datetime.utcfromtimestamp(timestamp)


def utc_from_sec(sec):
    """
    Calculate UTC time from seconds.
    Restricted to years in 1970 through 2038.
    :param sec: floating point number of seconds
    :return:
    """
    return datetime.datetime.utcfromtimestamp(sec)


def utc_from_ms(ms):
    """
    Calculate UTC time from milliseconds.
    Restricted to years in 1970 through 2038.
    :param ms: floating point number of milliseconds
    :return:
    """
    return datetime.datetime.utcfromtimestamp(ms / 1000)


def utc_future(**kwargs):
    """
    Get UTC datetime in the future.
    :param kwargs: supports [seconds, microseconds, milliseconds, minutes, hours,
            days, weeks, years, months]
    :return:
    """
    return datetime.datetime.utcnow() + relativedelta(**kwargs)


def datetime_add(dt, **kwargs):
    """
    Add some period to the datetime.
    :param dt: the datetime
    :param kwargs: supports [seconds, microseconds, milliseconds, minutes, hours,
            days, weeks, years, months]
    :return:
    """
    return dt + relativedelta(**kwargs)


def datetime_add_duration(dt, duration):
    """
    Add some duration to the datetime.
    :param dt: the datetime
    :param duration: can be '3 months', '100 days', '1 year'
    :return:
    """
    value, unit = parse_duration(duration)
    return dt + relativedelta(**{unit + 's': value})


def utc_time_expired(start_time, **kwargs):
    """
    Check if the datetime has expired.
    :param start_time: the datetime to check.
    :param kwargs:
    :return:
    """
    if isinstance(start_time, (datetime.datetime, datetime.date)):
        return start_time + relativedelta(**kwargs) < datetime.datetime.utcnow()
    else:
        return utc_from_sec(start_time) + relativedelta(**kwargs) < datetime.datetime.utcnow()


def parse(datetime_str, format=None):
    """
    Parse a datetime from string.
    :param datetime_str:
    :param format: sample value %Y-%m-%d %H:%M:%S
        see https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    :return:
    """
    if not format:
        return dateparser.parse(datetime_str)
    else:
        return datetime.datetime.strptime(datetime_str, format)


def format(datetime_value, format=None, timespec=None):
    """
    Format a datetime value.
    :param datetime_value:
    :param format:
    :param timespec:
    :return:
    """
    if not format:
        if not timespec:
            return datetime_value.isoformat(sep=' ')
        else:
            return datetime_value.isoformat(sep=' ', timespec=timespec)
    else:
        return datetime_value.strftime(format)


def normalize_unit(unit):
    """
    Normalize date time unit.
    :param unit: can be 'months', 'day', 'years', 'secs'
    :return: One of 'millisecond', 'second', 'minute', 'hour'
        'day', 'week', 'month', 'year'
    """
    time_unit = unit.strip().lower()
    if time_unit in ('seconds', 'second', 'secs', 'sec'):
        return 'second'
    if time_unit in ('minutes', 'minute', 'mins', 'min'):
        return 'minute'
    if time_unit in ('hours', 'hour'):
        return 'hour'
    if time_unit in ('days', 'day'):
        return 'day'
    if time_unit in ('weeks', 'weeks'):
        return 'week'
    if time_unit in ('months', 'month'):
        return 'month'
    if time_unit in ('years', 'year'):
        return 'year'
    raise TypeError('Unrecognized time unit: ' + time_unit)


def parse_duration(duration, target_unit=None):
    """
    Parse a duration such as "3 months", "1 years".
    :param duration:
    :param target_unit: convert to target unit, e.g. from 'year' to 'month'.
        With input "2 years", target_unit="month", output will be (24, "month").
    :return: a tuple of (amount, unit) such as (3, "month")
    """
    parts = duration.split(' ')
    parts = [x for x in parts if len(x)]  # parts = [x for x in filter(len, parts)]
    if len(parts) > 2:
        raise ValueError('Unrecognized duration value: ' + duration)

    value = int(parts[0])
    unit = normalize_unit(parts[1])

    if not target_unit or target_unit == unit:
        return value, unit

    mapping = {
        'year_month': 12,
        'month_year': 1 / 12.0,
        'week_day': 7,
        'week_hour': 7 * 24,
        'week_minute': 7 * 24 * 60,
        'week_second': 7 * 24 * 60 * 60,
        'day_week': 1 / 7.0,
        'day_hour': 24,
        'day_minute': 24 * 60,
        'day_second': 24 * 60 * 60,
        'hour_week': 1 / (24.0 * 7.0),
        'hour_day': 1 / 24.0,
        'hour_minute': 60,
        'hour_second': 60 * 60,
        'minute_week': 1 / (60.0 * 24.0 * 7.0),
        'minute_day': 1 / (60.0 * 24.0),
        'minute_hour': 1 / 60.0,
        'minute_second': 60,
        'second_week': 1 / (60.0 * 60.0 * 24.0 * 7.0),
        'second_day': 1 / (60.0 * 60.0 * 24.0),
        'second_hour': 1 / (60.0 * 60.0),
        'second_minute': 1 / 60.0,
    }
    factor = mapping.get(unit + '_' + target_unit)
    if factor is not None:
        return value * factor, target_unit
    raise ValueError('Unable to convert datetime unit from {} to {}'.format(unit, target_unit))
