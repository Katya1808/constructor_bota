from rest_framework import serializers
from .models import Bot, Scenario, Step, BotUser


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'order', 'step_type', 'content', 'next_step', 'conditions', 'created_at']


class ScenarioSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)
    steps_count = serializers.IntegerField(source='steps.count', read_only=True)

    class Meta:
        model = Scenario
        fields = ['id', 'bot', 'name', 'description', 'trigger', 'is_active',
                  'scenario_data', 'steps', 'steps_count', 'created_at', 'updated_at']


class BotSerializer(serializers.ModelSerializer):
    scenarios = ScenarioSerializer(many=True, read_only=True)
    scenarios_count = serializers.IntegerField(source='scenarios.count', read_only=True)

    class Meta:
        model = Bot
        fields = ['id', 'owner', 'name', 'description', 'platform', 'token',
                  'status', 'settings', 'scenarios', 'scenarios_count',
                  'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Автоматически устанавливаем владельца
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = ['id', 'bot', 'external_id', 'name', 'metadata',
                  'current_scenario', 'current_step', 'last_active', 'created_at']