from django.conf import settings


def site_meta(request):
    match = getattr(request, "resolver_match", None)
    is_home = bool(match and match.namespace == "pages" and match.url_name == "home")
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_CODE": settings.SITE_CODE,
        "AUTHOR_NAME": settings.AUTHOR_NAME,
        "AUTHOR_ID": settings.AUTHOR_ID,
        "VKR_TOPIC": settings.VKR_TOPIC,
        "is_home": is_home,
        "breadcrumbs": getattr(request, "breadcrumbs", []),
    }
