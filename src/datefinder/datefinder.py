import copy
import logging
import regex as re
from datetime import timedelta
from datetime import datetime as dt
from dateutil import tz, parser

from datefinder.constants import *

logger = logging.getLogger('datefinder')


class DateFinder(object):
    """
    Locates dates in a text
    """

    def __init__(self, base_date=None):
        self.base_date = base_date

    def find_dates(self, text, source=False, index=False, capture=False, strict=False):

        # Append text with a delimiter to make inputs consisting of solely a date work
        text = text + ' '

        for date_string, indices, captures in self.extract_date_strings(text, strict=strict):

            as_dt = self.parse_date_string(date_string, captures)
            if as_dt is None:
                # Dateutil couldn't make heads or tails of it
                # move on to next
                continue

            returnables = (as_dt,)
            if source:
                returnables = returnables + (date_string,)
            if index:
                returnables = returnables + (indices,)
            if capture:
                returnables = returnables + (captures,)
            if len(returnables) == 1:
                returnables = returnables[0]
            yield returnables

    def _find_and_replace(self, date_string, captures):
        """
        :warning: when multiple tz matches exist the last sorted capture will trump
        :param date_string:
        :return: date_string, tz_string
        """
        # add timezones to replace
        cloned_replacements = copy.copy(REPLACEMENTS)  # don't mutate
        for tz_string in captures.get('timezones', []):
            cloned_replacements.update({tz_string: ' '})

        date_string = date_string.lower()
        for key, replacement in cloned_replacements.items():
            # we really want to match all permutations of the key surrounded by whitespace chars except one
            # for example: consider the key = 'to'
            # 1. match 'to '
            # 2. match ' to'
            # 3. match ' to '
            # but never match r'(\s|)to(\s|)' which would make 'october' > 'ocber'
            date_string = re.sub(r'(^|\s)' + key + '(\s|$)', replacement, date_string, flags=re.IGNORECASE)

        return date_string, self._pop_tz_string(sorted(captures.get('timezones', [])))

    def _pop_tz_string(self, list_of_timezones):
        try:
            tz_string = list_of_timezones.pop()
            # make sure it's not a timezone we
            # want replaced with better abbreviation
            return TIMEZONE_REPLACEMENTS.get(tz_string, tz_string)
        except IndexError:
            return ''

    def _add_tzinfo(self, datetime_obj, tz_string):
        """
        take a naive datetime and add dateutil.tz.tzinfo object

        :param datetime_obj: naive datetime object
        :return: datetime object with tzinfo
        """
        if datetime_obj is None:
            return None

        tzinfo_match = tz.gettz(tz_string)
        return datetime_obj.replace(tzinfo=tzinfo_match)

    def parse_date_string(self, date_string, captures):
        # For well formatted string, we can already let dateutils parse them
        # otherwise self._find_and_replace method might corrupt them
        try:
            as_dt = parser.parse(date_string, default=self.base_date)
        except ValueError:
            # replace tokens that are problematic for dateutil
            date_string, tz_string = self._find_and_replace(date_string, captures)

            # One last sweep after removing
            date_string = date_string.strip(STRIP_CHARS)
            # Match strings must be at least 3 characters long
            # < 3 tends to be garbage
            if len(date_string) < 3:
                return None

            try:
                logger.debug('Parsing {0} with dateutil'.format(date_string))
                as_dt = parser.parse(date_string, default=self.base_date)
            except Exception as e:
                logger.debug(e)
                as_dt = None
            if tz_string:
                as_dt = self._add_tzinfo(as_dt, tz_string)
        return as_dt

    def extract_date_strings(self, text, strict=False):
        """
        Scans text for possible datetime strings and extracts them
        :param text:
        :param strict: Strict mode will only return dates sourced with day, month, and year
        """
        for match in DATE_REGEX.finditer(text):
            match_str = match.group(0)
            indices = match.span(0)

            # Get individual group matches
            captures = match.capturesdict()
            # time = captures.get('time')
            years = captures.get('years')
            digits = captures.get('digits')
            # digits_modifiers = captures.get('digits_modifiers')
            # days = captures.get('days')
            months = captures.get('months')
            # timezones = captures.get('timezones')
            # delimiters = captures.get('delimiters')
            # time_periods = captures.get('time_periods')
            # extra_tokens = captures.get('extra_tokens')
            undelimited_stamps = captures.get('undelimited_stamps')

            if strict:
                complete = False
                # eg 12-05-2015
                if len(digits) == 3:
                    complete = True
                # eg 19 February 2013 year 09:10
                elif (len(months) == 1) and (len(digits) == 2):
                    complete = True
                elif all([len(stamp) > 5 for stamp in undelimited_stamps]) and len(undelimited_stamps) > 0:
                    complete = True
                if not complete:
                    continue

            # Sanitize date_string
            # Replace unhelpful whitespace characters with single whitespace
            match_str = re.sub('[\n\t\s\xa0]+', ' ', match_str)

            # Add whitespace delimiters to undelimited stamps
            for stamp in undelimited_stamps:
                if len(stamp) > 7:
                    match_str = re.sub(stamp, stamp[0:4] + ' ' + stamp[4:6] + ' ' + stamp[6:], match_str)
                elif len(stamp) > 5:
                    match_str = re.sub(stamp, stamp[0:4] + ' ' + stamp[4:6] + ' ', match_str)

            # If the leading or trailing characters are delimiters, bump the indices and strip
            ind0 = indices[0]
            ind1 = indices[1]
            if match_str[0] in STRIP_CHARS:
                ind0 = ind0 + 1
            if match_str[-1] in STRIP_CHARS:
                ind1 = ind1 - 1
            indices = (ind0, ind1)
            match_str = match_str.strip(STRIP_CHARS)

            # Save sanitized source string
            yield match_str, indices, captures


class TimedeltaParser:

    def __init__(self, default_month=30, default_year=365.25,
                 ambiguous_month=True):
        """

        :param default_month: length of a month in days
        :param default_year: length of a year in days
        :param ambiguous_month:
            if unsure what "m" means, should it be month? False = minute
        """
        self.default_month = default_month
        self.default_year = default_year
        self.ambiguous_month = ambiguous_month
        self.found_year = False
        self.found_month = False
        self.found_hour = False
        self.found_minute = False

    def find_timedeltas(self, text):
        """
        Primary entry point for searching for a series of timedeltas
            in a string of text.
        :param text:
        :return:
        """
        for m in UNIT_RX.finditer(text):
            # for each timedelta, use these heuristics to determine
            #  whether or not an "m" is month/minute
            positive = True
            if m.group('relative_neg_post'):
                positive = False
            self._reset_timespans()
            td = timedelta(0)
            for section in EXTRACT_RX.finditer(m.group()):
                new_td, is_new = self.get_timedelta(section)
                if is_new:  # a new timedelta was found
                    yield td
                    td = new_td
                else:
                    td += new_td
            yield td if positive else -td

    def _reset_timespans(self):
        self.found_year = False
        self.found_month = False
        self.found_hour = False
        self.found_minute = False

    def _is_month(self):
        """
        Heuristics to determine whether or not "m" means minute or month
        :return:
        """
        if self.found_month:
            return False
        elif self.found_minute:
            return True
        elif self.found_hour:
            return False
        elif self.found_year:
            return True
        else:
            return self.ambiguous_month

    def get_timedelta(self, td_str):
        """
        Analyze a string containing only a timedelta.
        :param td_str: a string containing only timedelta elements
        :return:
            timedelta
            is_new: True if timedelta represents a new instance
        """
        # interpretation
        td = timedelta(0)
        is_new = False
        # resolve numeric
        number = int(td_str.group('number'))
        if td_str.group('fraction'):
            fract = td_str.group('fraction')
            if '/' in fract:
                n, d = fract.split('/')
                number += (float(n) / float(d))
            else:  # decimal
                number += float(fract)
        # resolve unit
        if td_str.group('second'):
            td = timedelta(seconds=number)
        elif td_str.group('minute') or (td_str.group('ambig') and not self._is_month()):
            if self.found_minute:  # if hour already found, start new td
                self._reset_timespans()
                is_new = True
            self.found_minute = True
            td = timedelta(minutes=number)
        elif td_str.group('hour'):
            if self.found_hour:  # if hour already found, start new td
                self._reset_timespans()
                is_new = True
            self.found_hour = True
            td = timedelta(hours=number)
        elif td_str.group('day'):
            td = timedelta(days=number)
        elif td_str.group('week'):
            td = timedelta(weeks=number)
        elif td_str.group('month') or (td_str.group('ambig') and self._is_month()):
            if self.found_month:  # if hour already found, start new td
                self._reset_timespans()
                is_new = True
            self.found_month = True
            td = timedelta(days=number * self.default_month)
        elif td_str.group('year'):
            if self.found_year:  # if hour already found, start new td
                self._reset_timespans()
                is_new = True
            self.found_year = True
            td = timedelta(days=number * self.default_year)
        return td, is_new


def find_dates(
        text,
        source=False,
        index=False,
        capture=False,
        strict=False,
        base_date=dt(1900, 1, 1),  # default to start of month
        index_date=None
):
    """
    Extract datetime strings from text

    :param capture:
    :param index_date:
        Index date to add any found timestamps to; if None, don't look for timestamps
    :param text:
        A string that contains one or more natural language or literal
        datetime strings
    :type text: str|unicode
    :param source:
        Return the original string segment
    :type source: boolean
    :param index:
        Return the indices where the datetime string was located in text
    :type index: boolean
    :param strict:
        Only return datetimes with complete date information. For example:
        `July 2016` of `Monday` will not return datetimes.
        `May 16, 2015` will return datetimes.
    :type strict: boolean
    :param base_date:
        Set a default base datetime when parsing incomplete dates
    :type base_date: datetime

    :return: Returns a generator that produces :mod:`datetime.datetime` objects,
        or a tuple with the source text and index, if requested
    """
    date_finder = DateFinder(base_date=base_date)
    for date in date_finder.find_dates(text, source=source, index=index, capture=capture, strict=strict):
        yield date
    for td in TimedeltaParser().find_timedeltas(text):
        yield td + index_date if index_date else td
