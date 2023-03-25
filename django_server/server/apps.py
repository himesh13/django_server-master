from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ElasticConfig(AppConfig):
    name = "django_server.server"
    verbose_name = _("server")
