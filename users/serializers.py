from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import  Team, ContactMessage

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'password', 'first_name',
                  'last_name', 'address', 'phone_number']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name = 'CustomUser'
        fields = ['id', 'email', 'first_name',
                  'last_name', 'address', 'phone_number']
        

        
class TeamSerializer(serializers.ModelSerializer):
    class Meta():
        model = Team
        fields = ['id', 'name', 'members', 'created_at', 'updated_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta():
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']

