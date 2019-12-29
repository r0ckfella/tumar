from rest_framework import serializers

from .models import Farm, Animal, Geolocation, Machinery, Event


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ('id', 'farm', 'imei', 'tag_number', 'name', 'updated', 'imsi', 'battery_charge', 'status',)


class MachinerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Machinery
        fields = ('id', 'farm', 'type', 'machinery_code',)


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ('id', 'user', 'iin', 'legal_person', 'requisites', 'breeding_stock', 'calves_number', 'cadastres',
                  'cadastre_land',)


class FarmAnimalsSerializer(FarmSerializer):
    animals = AnimalSerializer(many=True, read_only=True)

    class Meta(FarmSerializer.Meta):
        fields = FarmSerializer.Meta.fields + ('animals',)


class GeolocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geolocation
        fields = ('id', 'position', 'time',)


class GeolocationAnimalSerializer(GeolocationSerializer):
    animal = AnimalSerializer()

    class Meta(GeolocationSerializer.Meta):
        fields = GeolocationSerializer.Meta.fields + ('animal',)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'time', 'description', 'completed', 'animal',)


class EventAnimalSerializer(EventSerializer):
    imei = serializers.CharField(source='animal.imei')
    tag_number = serializers.CharField(source='animal.tag_number')

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ('tag_number', 'imei',)
