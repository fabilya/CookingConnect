from re import match as re_match

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username(value):
    if not re_match(r'^[\w.@+-]+$', value):
        raise ValidationError('username содержит недопустимые символы!')
    return value


class UsernameFieldValidator(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if not re_match(r'^[\w.@+-]+$', data):
            raise serializers.ValidationError(
                'username содержит недопустимые символы!'
            )
        return data
