from rest_framework import serializers

from .models import (
    BreedingStockEvent,
    CalfEvent,
    SingleBreedingStockEvent,
    SingleCalfEvent,
)
from ..animals.models import BreedingStock, Calf
from .utils import merge_events


class BreedingStockNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreedingStock
        fields = (
            "id",
            "tag_number",
            "name",
        )


class SingleBreedingStockEventSerializer(serializers.ModelSerializer):
    animal = BreedingStockNestedSerializer(read_only=True)

    class Meta:
        model = SingleBreedingStockEvent
        fields = (
            # "id",
            "animal",
            "completed",
            "completion_date",
            "attributes",
        )


class CalfNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calf
        fields = (
            "id",
            "tag_number",
            "name",
            "gender",
        )


class SingleCalfEventSerializer(serializers.ModelSerializer):
    animal = CalfNestedSerializer(read_only=True)

    class Meta:
        model = SingleCalfEvent
        fields = (
            # "id",
            "animal",
            "completed",
            "completion_date",
            "attributes",
        )


class BreedingStockEventSerializer(serializers.ModelSerializer):
    animals = SingleBreedingStockEventSerializer(
        source="singlebreedingstockevent_set", many=True, read_only=True
    )
    animals_list = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=BreedingStock.objects.all(), many=True,
    )

    class Meta:
        model = BreedingStockEvent
        fields = (
            "id",
            "title",
            "scheduled_date_range",
            "report",
            "type",
            "animals_list",
            "animals",
        )
        read_only_fields = (
            "id",
            "animals",
        )

    def create(self, validated_data):
        animals_list = validated_data.pop("animals_list", [])
        the_farm = self.context["request"].user.farm
        bs_event = BreedingStockEvent(**validated_data)

        merge_events(BreedingStockEvent, SingleBreedingStockEvent, bs_event, the_farm)

        # Create additional animals for bs_event
        for pk in animals_list:
            SingleBreedingStockEvent.objects.get_or_create(event=bs_event, animal=pk)

        return bs_event

    def update(self, instance, validated_data):
        animals_list = validated_data.pop("animals_list", None)
        the_farm = self.context["request"].user.farm

        if "id" in validated_data:
            validated_data.pop("id")  # remove id, since we already have instance obj
        instance = super(BreedingStockEventSerializer, self).update(
            instance, validated_data
        )

        if animals_list is not None:
            SingleBreedingStockEvent.objects.filter(event=instance).exclude(
                animal__in=animals_list
            ).delete()
            for animal_pk in animals_list:
                SingleBreedingStockEvent.objects.get_or_create(
                    event=instance, animal=animal_pk
                )

        merge_events(BreedingStockEvent, SingleBreedingStockEvent, instance, the_farm)

        return instance


# class BreedingStockEventAnimalSerializer(EventSerializer):
#     tag_number = serializers.CharField(source='animal.tag_number')

#     class Meta(EventSerializer.Meta):
#         fields = EventSerializer.Meta.fields + ('tag_number',)


class CalfEventSerializer(serializers.ModelSerializer):
    animals = SingleCalfEventSerializer(
        source="singlecalfevent_set", many=True, read_only=True
    )
    animals_list = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Calf.objects.all(), many=True
    )

    class Meta:
        model = CalfEvent
        fields = (
            "id",
            "title",
            "scheduled_date_range",
            "report",
            "type",
            "animals",
            "animals_list",
        )
        read_only_fields = ("id", "animals")

    def create(self, validated_data):
        animals_list = validated_data.pop("animals_list", [])
        the_farm = self.context["request"].user.farm
        calf_event = CalfEvent(**validated_data)

        merge_events(CalfEvent, SingleCalfEvent, calf_event, the_farm)

        for pk in animals_list:
            SingleCalfEvent.objects.get_or_create(event=calf_event, animal=pk)

        return calf_event

    def update(self, instance, validated_data):
        animals_list = validated_data.pop("animals_list", None)
        the_farm = self.context["request"].user.farm

        if "id" in validated_data:
            validated_data.pop("id")  # remove id, since we already have instance obj
        instance = super(CalfEventSerializer, self).update(instance, validated_data)

        if animals_list is not None:
            SingleCalfEvent.objects.filter(event=instance).exclude(
                animal__in=animals_list
            ).delete()
            for animal_pk in animals_list:
                # instance.animals.add(animals_list)
                SingleCalfEvent.objects.get_or_create(event=instance, animal=animal_pk)

        merge_events(CalfEvent, SingleCalfEvent, instance, the_farm)

        return instance
