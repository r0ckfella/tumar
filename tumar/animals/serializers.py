from django.db import connections
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_gis import serializers as geo_serializers

from .models import Farm, Animal, Geolocation, Machinery, Event, Cadastre, BreedingStock, BreedingBull, Calf, StoreCattle


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ('id', 'farm', 'imei', 'tag_number', 'name', 'updated',
                  'imsi', 'battery_charge', 'status', 'image',)
        read_only_fields = ('id', 'updated', 'status', 'battery_charge',)

class BreedingStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreedingStock
        fields = ('id', 'farm', 'tag_number', 'name', 'birth_date', 'image', 'breed',)
        read_only_fields = ('id',)

class CalfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calf
        fields = ('id', 'farm', 'tag_number', 'name', 'birth_date',
                  'image', 'breed', 'wean_date', 'gender', 'mother')
        read_only_fields = ('id',)

class BreedingBullSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreedingBull
        fields = ('id', 'farm', 'tag_number', 'name', 'birth_date',
                  'image', 'breed', 'birth_place',)
        read_only_fields = ('id',)

class StoreCattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCattle
        fields = ('id', 'farm', 'tag_number', 'name', 'birth_date',
                  'image', 'wean_date',)
        read_only_fields = ('id',)


class CadastreSerializer(serializers.ModelSerializer):
    # since drf has a bug with required=True
    geometry = geo_serializers.GeometryField(source='geom', required=False)

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
        fields = ('id', 'user', 'iin', 'legal_person', 'iik', 'bank', 'bin', 'address',
                  'calves_number',)
        read_only_fields = ('calves_number',)


class CreateFarmSerializer(serializers.ModelSerializer):
    cadastres = serializers.ListField()

    class Meta:
        model = Farm
        fields = ('id', 'iin', 'legal_person', 'iik', 'bank', 'bin', 'address', 'cadastres',)

    def to_representation(self, instance):
        serializer = FarmCadastresSerializer(instance)
        return serializer.data

    def create(self, validated_data):
        cadastres = validated_data.pop('cadastres')
        validated_data['user'] = self.context['request'].user
        farm = Farm.objects.create(**validated_data)

        for cad_number in cadastres:
            Cadastre.objects.create(farm=farm, cad_number=cad_number)

        return farm


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
