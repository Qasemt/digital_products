from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Profile
        fields = (
            "id",
            "first_name",
            "last_name",
            "birthday",
            "mobile_number",
            "image_url",
        )

    #   URL_FIELD_NAME = 'image'
