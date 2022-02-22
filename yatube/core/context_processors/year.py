import datetime


def year(request):
    actual_year = datetime.datetime.now().year
    return {'year': actual_year}
