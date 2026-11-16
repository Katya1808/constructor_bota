from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'bots', views.BotViewSet, basename='bot')
router.register(r'scenarios', views.ScenarioViewSet, basename='scenario')
router.register(r'bot-users', views.BotUserViewSet, basename='botuser')

urlpatterns = [
    path('', include(router.urls)),

    # Вложенные маршруты для шагов сценария
    path('scenarios/<int:scenario_pk>/steps/',
         views.StepViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='step-list'),
    path('scenarios/<int:scenario_pk>/steps/<int:pk>/',
         views.StepViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='step-detail'),
]