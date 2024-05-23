from rest_framework import serializers


class ScheduleRequestSerializer(serializers.Serializer):
    date = serializers.CharField()
    group = serializers.CharField()

class ScheduleTeacherSeriaizer(serializers.Serializer):
    date = serializers.CharField()
    group = serializers.CharField()