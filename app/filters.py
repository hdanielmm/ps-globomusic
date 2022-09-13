from babel import dates
from flask import g

# Date formatting Jinja2 filter
def date_format(value):
    return dates.format_date(value, locale=g.lang)