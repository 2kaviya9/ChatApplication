from rest_framework import serializers

from users.models import User, ChatBot, UserConnect

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as JWTTokenSerializer,
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_superuser", "profile")
        
    def to_representation(self, instance):
        # Call the parent method to get the standard representation
        representation = super().to_representation(instance)
        request = self.context.get('request')
        print(request.user.pk,  "***")
        from django.db.models import Q
        user_connection = UserConnect.objects.filter((Q(user = instance.pk) & Q(connected_user = request.user.pk)) |
                                                     Q(user = request.user.pk) & Q(connected_user = instance.pk))
        if user_connection.filter(is_approved = True):
            representation['request'] =  'Approved'
        elif user_connection.filter(requested_by = request.user.pk) and user_connection.filter(is_approved = False):
            representation['request'] = 'Waiting for approval'
        elif  user_connection.filter(is_approved = False):
            representation['request'] = 'Pending Request'
        else:
            representation['request'] = 'Not Connected'
        
        return representation
        
        
class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = ("id", "username", "email", "is_superuser", "profile")
        
    def validate(self, attrs):
        user_connect = UserConnect.objects.filter(user = attrs["sender"], connected_user = attrs["receiver"], is_approved = False).first()
        first_obj = ChatBot.objects.filter(sender = attrs["sender"], connected_user = attrs["receiver"]).exists()
        if not first_obj:
            if not user_connect:
                serializers.ValidationError({"error": "Your request was not approved yet."})
            else:
                serializers.ValidationError({"error": "Please send the request message."})
        return attrs
    
    


class UserConnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConnect
        fields = '__all__'



class UserConnectGeterializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    connected_user = serializers.SerializerMethodField()
    requested_by = serializers.SerializerMethodField()
    class Meta:
        model = UserConnect
        fields = '__all__'
        
    def get_user(self, obj):
        return{
            "id" : obj.user.pk,
            "username" : obj.user.username
        }
    def get_connected_user(self, obj):
        return{
            "id" : obj.connected_user.pk,
            "username" : obj.connected_user.username
        }
    def get_requested_by(self, obj):
        return{
            "id" : obj.requested_by.pk,
            "requested_byname" : obj.user.username
        }
        
        
class TokenObtainPairSerializer(JWTTokenSerializer):
    """The custom serializer used to obtain a JSON web token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token
