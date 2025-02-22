from contextlib import suppress

import pytz
from django.utils.timezone import activate


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get("django_timezone")
        if tzname:
            with suppress(pytz.UnknownTimeZoneError):
                activate(pytz.timezone(tzname))
        return self.get_response(request)
