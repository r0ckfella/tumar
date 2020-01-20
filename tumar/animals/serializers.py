from django.db import connections
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_gis import serializers as geo_serializers

from .models import Farm, Animal, Geolocation, Machinery, Event, Cadastre


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ('id', 'farm', 'imei', 'tag_number', 'name', 'updated', 'imsi', 'battery_charge', 'status',)
        read_only_fields = ('id', 'updated', 'status', 'battery_charge',)


class CadastreSerializer(serializers.ModelSerializer):
    geometry = geo_serializers.GeometryField(source='geom', required=False)  # since drf has a bug with required=True

    class Meta:
        model = Cadastre
        fields = ('id', 'title', 'cad_number', 'geometry', 'farm',)


class MachinerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Machinery
        fields = ('id', 'farm', 'type', 'machinery_code',)


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ('id', 'user', 'iin', 'legal_person', 'requisites', 'breeding_stock', 'calves_number',)


class FarmAnimalsSerializer(FarmSerializer):
    animals = AnimalSerializer(many=True, read_only=True)

    class Meta(FarmSerializer.Meta):
        fields = FarmSerializer.Meta.fields + ('animals',)


class FarmCadastresSerializer(FarmSerializer):
    cadastres = CadastreSerializer(many=True, read_only=True)

    class Meta(FarmSerializer.Meta):
        fields = FarmSerializer.Meta.fields + ('cadastres',)


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
