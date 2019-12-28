from django.forms.models import model_to_dict
from django.test import TestCase
from nose.tools import eq_, ok_

from .factories import FarmFactory
from ..serializers import FarmSerializer
from ...users.models import User
from ...users.test.factories import UserFactory


class TestFarmSerializer(TestCase):

    def setUp(self):
        temp_user = UserFactory()
        self.farm_data = model_to_dict(FarmFactory.build(user=temp_user))

    def test_serializer_with_empty_data(self):
        serializer = FarmSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = FarmSerializer(data=self.farm_data)
        result = serializer.is_valid()
        ok_(result)
