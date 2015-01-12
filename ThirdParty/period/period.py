#!/usr/bin/env python
# $Id: period.py,v 2.5 2002-01-07 11:07:57-06 annis Exp $
# $Source: /u/annis/code/python/lib/period/RCS/period.py,v $
#
# Copyright (c) 2001 - 2002 William S. Annis.  All rights reserved.
# This is free software; you can redistribute it and/or modify it
# under the same terms as Perl (the Artistic Licence).  Developed at
# the Department of Biostatistics and Medical Informatics, University
# of Wisconsin, Madison.
 
"""Deal with time periods

The single function in_period(time, period) determines if a given time
period string matches the time given.  The syntax is based loosely on
the class specifications used in Cfengine (http://www.iu.hioslo.no/cfengine).
"""

import string
import re
import time
import os

WEEK_MAP = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday']
MONTH_MAP = ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
DAYTYPE_MAP = ['Weekday', 'Weekend']


# Used by the PeriodParser class.
def _remove_otiose(lst):
    """lift deeply nested expressions out of redundant parentheses"""
    listtype = type([])
    while type(lst) == listtype and len(lst) == 1:
        lst = lst[0]

    return lst


class PeriodParser:
    """Parse time period specifications."""
    def __init__(self):
        self.SPECIAL = "().|!"
        pass

    def parse(self, str=None):
        if str:
            self.str = str
            self.i = 0
            self.len = len(str)
            self.level = 0

        expr = []
        tok = self.get_token()
        while tok != '':
            if tok == ')':
                self.level = self.level - 1
                if self.level < 0:
                    break    # too many closing parens... catch error below
                else:
                    return expr
            elif tok == '(':
                self.level = self.level + 1
                sexpr = _remove_otiose(self.parse())
                expr.append(sexpr)
            else:
                expr.append(tok)

            tok = self.get_token()

        # If the level isn't correct, then some extra parens are
        # involved.  Complain about that.
        if self.level == 0:
            return expr
        elif self.level > 0:
            raise Exception, "mismatched opening parenthesis in expression"
        else:
            raise Exception, "mismatched closing parenthesis in expression"

    def get_token(self):
        if self.i >= self.len:
            return ''

        if self.str[self.i] in self.SPECIAL:
            self.i = self.i + 1
            return self.str[self.i - 1]
        else:
            tok = ""
            while self.i < self.len - 1:
                if self.str[self.i] in self.SPECIAL:
                    break
                else:
                    tok = tok + self.str[self.i]
                    self.i = self.i + 1

            if not self.str[self.i] in self.SPECIAL:
                tok = tok + self.str[self.i]
                self.i = self.i + 1

            return tok


# A basic stack... very convenient.
class Stack:
    def __init__(self):
        self.s = []

    def push(self, datum):
        self.s.append(datum)

    def pop(self):
        return self.s.pop()

    def empty(self):
        return len(self.s) == 0

    def __repr__(self):
        return `self.s`


# For determining the order of operations.
_precedence = {'.': 10,
               '|': 5,
               '!': 30}

#   This is a little scary, since I didn't avail myself of the several
# parser generator tools available for python, largely because I like
# my modules to be self-sufficient whenever possible.  Also, most of
# the generators are still in development.
#
#   The operations have a precedence.  Since I only make a single pass over
# the parsed tokens, I keep track of the number of items in a precedence
# group.  When an operator of higher precedence is seen, all the operations
# are popped off the op stack before any more reading takes place.  This
# ensures that members of a precedence group are evaluated together.
#   I take the same approach with unary operators.  After every item
# added to the syntax list I check for unary operators in that stack.
# This strange approach allows me to correctly negate sub-expressions.
# It might be the standard way of doing this... I don't know.  Perhaps
# some day I should take a compilers class.
class PeriodSyntax:
    def __init__(self):
        self.ops = [".", "|", "!"]      # To know operations.
        self.uops = ["!"]               # Unary operations.

    def flatten(self, lst=None):
        """syntax.flatten(token_stream) - compile period tokens

        This turns a stream of tokens into p-code for the trivial
        stack machine that evaluates period expressions in in_period.
        """
        tree = []
        uops = []                       # accumulated unary operations
        s = Stack()
        group_len = 0                   # in current precendence group
        for item in lst:
            if type(item) == type([]):
                # Subexpression.
                tree = tree + self.flatten(item)
                group_len = group_len + 1
                # Unary ops dump, for things like: '!(Monday|Wednesday)'
                for uop in uops:
                    tree.append(uop)
                uops = []
            elif item in self.ops and item not in self.uops:
                # Operator.
                if not s.empty():
                    prev_op = s.pop()
                    # If the precendence of the previous operation is
                    # higher then dump out everything so far, ensuring the
                    # order of evaluation.
                    if _precedence[prev_op] > _precedence[item]:
                        s.push(prev_op)  # put it back
                        for i in range(group_len - 1):
                            tree.append(s.pop())
                        group_len = 0
                    else:
                        s.push(prev_op)
                    s.push(item)
                else:
                    s.push(item)
            elif item in self.uops:
                uops.append(item)
            else:
                # Token of some sort.
                tree.append(item)
                group_len = group_len + 1
                # Dump any unary operations.
                for uop in uops:
                    tree.append(uop)
                uops = []

        while not s.empty():
            tree.append(s.pop())

        # Drop any remaining unary operations.
        for uop in uops:
            tree.append(uop)

        return tree


class _Time:
    """Utility class for symbolic date manipulation."""
    def __init__(self, tyme=None):
        if not tyme:
            self.time = time.localtime(time.time())
        else:
            self.time = time.localtime(tyme)

        self._set_props()

    def _set_props(self):
        (self.weekday,
         self.month,
         self.day,
         self.hr,
         self.minute,
         self.week,
         self.year) = string.split(time.strftime("%A %B %d %H %M %U %Y", self.time))

        if self.weekday in ['Saturday', 'Sunday']:
            self.daytype = 'Weekend'
        else:
            self.daytype = 'Weekday'


# For use in the in_period function.
_parser = PeriodParser()
_syntax = PeriodSyntax()

def in_period(period, tyme=None):
    now = _Time(tyme)
    periodcode = _syntax.flatten(_parser.parse(period))
    s = Stack()
    # Run the period code through a trivial stack machine.
    try:
        for item in periodcode:
            if item == '.':
                # Have to pre-pop, otherwise logical short-circuiting will
                # sometimes miss syntax errors like "Monday||Tuesday".
                a = s.pop()
                b = s.pop()
                s.push(a and b)
            elif item == '|':
                a = s.pop()
                b = s.pop()
                s.push(a or b)
            elif item == "!":
                s.push(not s.pop())
            else:
                s.push(_check_timespec(item, now))
    
        return s.pop()
    except IndexError:
        raise Exception, "bad period (too many . or | operators?): %s" % period


def _check_timespec(timespec, now):
    if timespec[0:2] == 'Yr':
        return now.year in _parse_Yr(timespec)
    elif timespec[0:2] == 'Hr':
        return now.hr in _parse_Hr(timespec)
    elif timespec[0:3] == 'Min':
        return now.minute in _parse_Min(timespec)
    elif timespec[0:3] == 'Day':
        return now.day in _parse_Day(timespec)
    elif timespec in WEEK_MAP:
        return now.weekday == timespec
    # Could be 'Week02' or 'Weekday' here.
    elif timespec[0:4] == 'Week':
        if timespec in DAYTYPE_MAP:
            return now.daytype == timespec
        else:
            return now.week in _parse_Week(timespec)
    elif timespec in MONTH_MAP:
        return now.month == timespec
    elif timespec == 'Always':
        return 1
    elif timespec == 'Never':
        return 0
    elif '-' in timespec:
        first = timespec[0:string.index(timespec,'-')]
        if first in MONTH_MAP:
            return now.month in _compose_symbolic_range('month', timespec)
        elif first in WEEK_MAP:
            return now.weekday in _compose_symbolic_range('weekday', timespec)
        else:
            raise Exception, "Bad range specification: %s" % timespec
    else:
        raise Exception, "Bad time specification: %s" % timespec


def _parse_Yr(year):
    """Return a hash of the matching years, coping with ranges."""
    return _compose_range("Yr", year, fill=4)

def _parse_Hr(hour):
    """Return a hash of the matching hours, coping with ranges."""
    return _compose_range("Hr", hour, fill=2)

def _parse_Min(min):
    """Return a hash of the matching days, coping with ranges."""
    return _compose_range("Min", min, fill=2)

def _parse_Day(day):
    """Return a hash of the matching days, coping with ranges."""
    return _compose_range("Day", day, fill=2)

def _parse_Week(week):
    """Return a hash of the matching weeks, coping with ranges."""
    return _compose_range("Week", week, fill=2)


def _compose_range(pattern, rule, fill=2):
    """oc._compose_range('Week', 'Week04-Week09', fill=2) - hash a range.

    This takes apart a range of times and returns a dictionary of
    all intervening values appropriately set.  The fill value is
    used to format the time numbers.
    """
    keys = []
    mask = len(pattern)
    for rule in string.split(rule, ","):
        if not '-' in rule:
            if rule[:mask] == pattern:
                keys.append(rule[mask:])
            else:
                keys.append(rule)
        else:
            (start, end) = string.split(rule, '-')
            if rule[:mask] == pattern:
                start = string.atoi(start[mask:])
            else:
                start = string.atoi(start)
            # Since I allow both "Week00-15" and "Week00-Week15", I need
            # to check for the second week.
            if end[0:mask] == pattern:
                end = string.atoi(end[mask:])
            else:
                end = string.atoi(end)
    
            key = "%%0%ii" % fill
            for i in range(start, end + 1):
                keys.append(key % i)
    
    #print keys
    return keys


def _compose_symbolic_range(pattern, rule):
    # Are we cycling through day or month names?
    if pattern == 'weekday':
        cycle = WEEK_MAP
    elif pattern == 'month':
        cycle = MONTH_MAP
    else:
        raise Exception, "Unknown cycle name: %s" % pattern

    # Length of the cycle (for modulo arithmetic).
    clen = len(cycle)

    keys = []
    for rule in string.split(rule, ","):
        if not '-' in rule:
            keys.append(rule)
        else:
            (start, end) = string.split(rule, '-')
            if not (start in cycle and end in cycle):
                raise Exception, "Unknown %s name: %s" % (pattern, rule)
            start_i = cycle.index(start)
            while cycle[start_i] != end:
                keys.append(cycle[start_i])
                start_i = (start_i + 1) % clen
            keys.append(cycle[start_i])        # Include the final member

    return keys


def is_holiday(now=None, holidays="/etc/acct/holidays"):
    """is_holiday({now}, {holidays="/etc/acct/holidays"}"""
    now = _Time(now)
    # Now, parse holiday file.
    if not os.path.exists(holidays):
        raise Exception, "There is no holidays file: %s" % holidays

    f = open(holidays, "r")
    # First, read all leading comments.
    line = f.readline()
    while line[0] == '*': line = f.readline()

    # We just got the year line.
    (year, primestart, primeend) = string.split(line)
    # If not the right year, we have no idea for certain.  Skip.
    if not year == now.year: return 0

    # Now the dates.  Check each against now.
    while line != '':
        # Of course, ignore comments.
        if line[0] == '*':
            line = f.readline()
            continue

        try:
            # Format: "1/1	New Years Day"
            (month, day) = string.split(string.split(line)[0], "/")
            # The _Time class has leading-zero padded day numbers.
            if len(day) == 1: day = '0' + day
            # Get month number from index map (compensate for zero indexing).
            month = MONTH_MAP[string.atoi(month) - 1]

            # Check the date.
            #print month, now.month, day, now.day
            if month == now.month and day == now.day:
                return 1

            line = f.readline()
        except:
            # Skip malformed lines.
            line = f.readline()
            continue

    # If no match found, we must not be in a holiday.
    return 0


if __name__ == '__main__':
    for a in ['Friday', 'Friday.January', 'Friday.January.Day04',
              'Friday.January.Day05',
              'Friday.January.Day02-12',
              'Friday.January.!Day02-12',
              'April.Yr1988-2001',
              '(January|April).Yr1988-2002',
              'May.Hr05-12',
              'Tuesday.Hr07-23',
              'January.Hr05-09,11-21',
              'Week00', 'Week02',
              '!Week00', '!Week02',
              'Hr12|Hr13|Hr14|Hr15', '(Hr12|Hr13|Hr14|Hr15)',
              'Weekday', 'Weekend',
              'Weekday.Min50-55',
              'Weekday.Min05-50',
              'Weekday.Hr07-23',
              'Monday-Friday',
              'December-February',
              'January-March.Monday-Friday',
              '!January-March.Monday-Friday',
              'January-March.!Weekend',
              '(Monday|Friday).Hr09-17',
              '!!!Weekday',
              '!!!!Weekday',
              '((((Yr2002))))',
              'Friday-Flopday',            # must fail
              'Monday||Tuesday',           # must fail
              '(Monday|Tuesday',           # must fail
              'Monday|Tuesday)',           # must fail
              '(Monday|Friday)).Hr09-17',  # must fail
              '(Monday|!(Weekday)).Hr11-14',
              '(Monday|(Weekday)).Hr11-14',
              '(Monday|(Friday.December-March)).Yr2002'
              ]:
        try:
            print "*", a, in_period(a)
        except Exception, e:
            print "ERR", e

    # Test holiday file.
    if os.path.exists("holidays"):
        print "*", "holiday", is_holiday(holidays="holidays")



# EOF
