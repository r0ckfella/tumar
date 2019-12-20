from rest_framework import serializers

from .models import Farm, Animal, Geolocation


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ('id', 'imei', 'cow_code',)
        read_only_fields = ('id', 'imei', 'cow_code',)


class AnimalFarmSerializer(AnimalSerializer):
    farm_name = serializers.CharField(source='farm.name')

    class Meta(AnimalSerializer.Meta):
        fields = AnimalSerializer.Meta.fields + ('farm_name',)
        read_only_fields = AnimalSerializer.Meta.read_only_fields + ('farm_name',)


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ('id', 'key', 'name',)
        read_only_fields = ('id', 'key', 'name',)


class FarmAnimalsSerializer(FarmSerializer):
    animals = AnimalSerializer(many=True, read_only=True)

    class Meta(FarmSerializer.Meta):
        fields = FarmSerializer.Meta.fields + ('animals',)
        read_only_fields = FarmSerializer.Meta.read_only_fields + ('animals',)


class GeolocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geolocation
        fields = ('id', 'time', 'position',)
        read_only_fields = ('id', 'time', 'position',)


class GeolocationAnimalSerializer(GeolocationSerializer):
    cow_code = serializers.CharField(source='animal.cow_code')

    class Meta(GeolocationSerializer.Meta):
        fields = ('cow_code',) + GeolocationSerializer.Meta.fields
        read_only_fields = ('cow_code',) + GeolocationSerializer.Meta.read_only_fields
