from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from django_server.server.api.views import (
    LoadDataFilesViewSet,
    LoadRetrainModel,
    TextInputViewSet,
    LoadFileViewSet,
    CollectFeedbackViewSet,
    LoadRetrainModel
)

app_name = "api/"
router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register(
    "/apply-ml",
    TextInputViewSet,
    "/apply-ml",
)

router.register(
    "/collect-feedback",
    CollectFeedbackViewSet,
    "/collect-feedback",
)

router.register(
    "/load-data-files",
    LoadDataFilesViewSet,
    "/load-data-files",
)
router.register(
    "/upload-file",
    LoadFileViewSet,
    "/upload-file",
)

router.register(
    "/retrain",
LoadRetrainModel,
    "/retrain",
)