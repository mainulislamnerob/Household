from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'password', 'first_name',
                  'last_name', 'address', 'phone_number']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name = 'CustomUser'
        fields = ['id', 'email', 'first_name',
                  'last_name', 'address', 'phone_number']
        
class ProfileSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name = 'Profile'
        fields = ['id', 'email', 'first_name',
                  'last_name', 'address', 'phone_number']
        
class TeamSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name = 'Team'
        fields = ['id', 'name', 'members', 'created_at', 'updated_at']

class ContactMessageSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name = 'ContactMessage'
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']

