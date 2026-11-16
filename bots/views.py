from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Bot, Scenario, Step, BotUser
from .serializers import BotSerializer, ScenarioSerializer, StepSerializer, BotUserSerializer


class BotViewSet(viewsets.ModelViewSet):
    """ViewSet для управления ботами"""
    serializer_class = BotSerializer

    def get_queryset(self):
        # Возвращаем только боты текущего пользователя
        return Bot.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Получение статистики бота"""
        bot = self.get_object()
        users_count = bot.bot_users.count()
        scenarios_count = bot.scenarios.count()

        return Response({
            'bot_id': bot.id,
            'total_users': users_count,
            'total_scenarios': scenarios_count,
            'active_scenarios': bot.scenarios.filter(is_active=True).count()
        })


class ScenarioViewSet(viewsets.ModelViewSet):
    """ViewSet для управления сценариями"""
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        queryset = Scenario.objects.all()
        bot_id = self.request.query_params.get('bot_id')
        if bot_id:
            queryset = queryset.filter(bot_id=bot_id)
        return queryset

    @action(detail=True, methods=['get'])
    def steps(self, request, pk=None):
        """Получение всех шагов сценария"""
        scenario = self.get_object()
        steps = scenario.steps.all()
        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data)


class StepViewSet(viewsets.ModelViewSet):
    """ViewSet для управления шагами сценария"""
    serializer_class = StepSerializer

    def get_queryset(self):
        return Step.objects.all()

    def perform_create(self, serializer):
        # Автоматически связываем шаг со сценарием из URL
        scenario_id = self.kwargs.get('scenario_pk')
        serializer.save(scenario_id=scenario_id)


class BotUserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet только для чтения пользователей бота"""
    serializer_class = BotUserSerializer

    def get_queryset(self):
        queryset = BotUser.objects.all()
        bot_id = self.request.query_params.get('bot_id')
        if bot_id:
            queryset = queryset.filter(bot_id=bot_id)
        return queryset
