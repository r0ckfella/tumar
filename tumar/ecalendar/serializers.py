from rest_framework import serializers

from .models import BreedingStockEvent, CalfEvent

class BreedingStockEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreedingStockEvent
        fields = ('id', 'title', 'scheduled_date', 'completion_date', 'report', 'type', 'completed', 'animal',)
        read_only_fields = ('id',)


# class BreedingStockEventAnimalSerializer(EventSerializer):
#     tag_number = serializers.CharField(source='animal.tag_number')

#     class Meta(EventSerializer.Meta):
#         fields = EventSerializer.Meta.fields + ('tag_number',)


class CalfEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalfEvent
        fields = ('id', 'title', 'scheduled_date', 'completion_date', 'report', 'type', 'completed', 'animal',)
        read_only_fields = ('id',)
