# Date formatting Jinja2 filter
def date_format(value, format="%m/%d/%Y"):
    return value.strftime(format)