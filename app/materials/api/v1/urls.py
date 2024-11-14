from django.urls import path, include
from rest_framework.routers import DefaultRouter

from materials.api.v1.views import (
    MaterialViewSet,
    CreateMaterialFromXLSX,
    CategoryViewSet,
)


router = DefaultRouter()
router.register(r'materials', MaterialViewSet, basename='materials')
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('', include(router.urls)),
    path('xlsx/', CreateMaterialFromXLSX.as_view()),
]