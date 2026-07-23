from django.http import HttpRequest, HttpResponse


def healthcheck(_: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")
