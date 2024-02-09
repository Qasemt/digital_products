from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Profile
        fields = ("id", "name", "last_name", "birthday", "mobile_number", "image")

    #   URL_FIELD_NAME = 'image'
