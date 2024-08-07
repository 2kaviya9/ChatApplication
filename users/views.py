from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from users.serializer import ChatBotSerializer, TokenObtainPairSerializer, UserConnectGeterializer, UserSerializer, UserConnectSerializer
from users.models import ChatBot, UserConnect
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from rest_framework.pagination import PageNumberPagination
# Create your views here.

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.contrib.auth.models import User
class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ("username",)
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * All users are able to access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = User.objects.exclude(id = request.user.pk)
        serializer = UserSerializer(usernames, many=True, context={'request': request})
        return Response(serializer.data)

    
    
class ChatBotViewset(viewsets.ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    

    
class UserConnectViewset(viewsets.ModelViewSet):
    queryset = UserConnect.objects.all()
    serializer_class = UserConnectGeterializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(Q(user = self.request.user.pk) | Q(connected_user = self.request.user.pk))
        return queryset
    
    
class RequestSendinView(APIView):
    permission_classes = (permissions.IsAuthenticated,)  # Ensure this is a tuple or list
    http_method_names = ["post",]

    def post(self, request):
        # Initialize the serializer with the data from the request
        if request.user.pk == request.data.get("user"):
            return Response({"error" : "Can not request themselves"}, 400)
        serializer = UserConnectSerializer(data={
            'user': request.user.id,
            'connected_user': request.data.get("user"),
            'requested_by': request.user.id
        })
        
        # Validate and save the data
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Message Request sent successfully"}, status=status.HTTP_201_CREATED)
        
        return Response({"error": "Something went wrong", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RequestApproverejectView(APIView):
    permission_classes = (permissions.IsAuthenticated,)  # Ensure this is a tuple or list
    http_method_names = ["put"]

    def put(self, request, pk):
        print("Hii")
        if request.user.pk == request.data.get("user"):
            return Response({"error" : "Can not approve themselves"}, 400)
        try:
            print(pk, "((()))")  # Debugging print statement
            instance = UserConnect.objects.get(pk=pk)
        except UserConnect.DoesNotExist:
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserConnectSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if not instance.is_approved:
                instance.delete()
            return Response({"message": "Message Request updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.views import TokenObtainPairView
class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data.get("refresh")
        username = request.data.get("username")

        if refresh:
            return super().post(request, *args, **kwargs)
        else:
            return Response(
                {"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )