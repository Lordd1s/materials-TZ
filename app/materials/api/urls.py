from django.urls import path, include

urlpatterns = [
    path('v1/', include('materials.api.v1.urls'))
]
