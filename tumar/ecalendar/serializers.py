from psycopg2.extras import DateRange
from rest_framework import serializers

from .models import (
    BreedingStockEvent,
    CalfEvent,
    SingleBreedingStockEvent,
    SingleCalfEvent,
)
from ..animals.models import BreedingStock, Calf


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
        bs_event = BreedingStockEvent(**validated_data)

        # Checking if there any similar event
        overlapping_events = BreedingStockEvent.objects.filter(
            title__icontains=bs_event.title[: len(bs_event.title) // 2],
            type=bs_event.type,
            scheduled_date_range__overlap=bs_event.scheduled_date_range,
        )

        for event in overlapping_events:
            bs_event.scheduled_date_range = DateRange(
                event.scheduled_date_range.lower
                if event.scheduled_date_range.lower
                < bs_event.scheduled_date_range.lower
                else bs_event.scheduled_date_range.lower,
                event.scheduled_date_range.upper
                if event.scheduled_date_range.upper
                > bs_event.scheduled_date_range.upper
                else bs_event.scheduled_date_range.upper,
            )

            bs_event.report = bs_event.report + " " + event.report

        bs_event.save()

        # Attach animals to bs_event
        SingleBreedingStockEvent.objects.filter(event__in=overlapping_events).update(
            event=bs_event
        )

        overlapping_events.exclude(pk=bs_event.pk).delete()

        # Create additional animals for bs_event
        for pk in animals_list:
            SingleBreedingStockEvent.objects.get_or_create(event=bs_event, animal=pk)

        return bs_event

    def update(self, instance, validated_data):
        animals_list = validated_data.pop("animals_list", None)

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
        calf_event = CalfEvent(**validated_data)

        # Checking if there any similar event
        overlapping_events = CalfEvent.objects.filter(
            title__icontains=calf_event.title[: len(calf_event.title) // 2],
            type=calf_event.type,
            scheduled_date_range__overlap=calf_event.scheduled_date_range,
        )

        for event in overlapping_events:
            calf_event.scheduled_date_range = DateRange(
                event.scheduled_date_range.lower
                if event.scheduled_date_range.lower
                < calf_event.scheduled_date_range.lower
                else calf_event.scheduled_date_range.lower,
                event.scheduled_date_range.upper
                if event.scheduled_date_range.upper
                > calf_event.scheduled_date_range.upper
                else calf_event.scheduled_date_range.upper,
            )

            calf_event.report = calf_event.report + " " + event.report

        calf_event.save()

        # Attach animals to calf_event
        SingleCalfEvent.objects.filter(event__in=overlapping_events).update(
            event=calf_event
        )

        overlapping_events.exclude(pk=calf_event.pk).delete()

        for pk in animals_list:
            SingleCalfEvent.objects.get_or_create(event=calf_event, animal=pk)

        return calf_event

    def update(self, instance, validated_data):
        animals_list = validated_data.pop("animals_list", None)

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

        return instance
