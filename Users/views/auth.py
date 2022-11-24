from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

from APIBackendService.views import BaseAppAPIView
from Users.serializers import (
    LoginUserQuerySerializer,
    UserCreateUpdateSerializer,
)
from Users.models import User


class AuthView(APIView):
    """
    Deprecated view for simple auth. Use common account login with accounts server
    """
    @swagger_auto_schema(
        operation_summary='Login',
        operation_description='Get authentication token for exists user',
        query_serializer=LoginUserQuerySerializer(),
        responses={
            200: 'User successfully authenticated',
            400: 'Bad request',
            401: 'Incorrect password',
            404: 'User not found',
        }
    )
    def get(self, request):
        serializer = LoginUserQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, username=serializer.validated_data['username'])
        user.last_login = timezone.now()
        user.save()

        if user.check_password(serializer.validated_data['password']):
            token, created = Token.objects.get_or_create(user=user)
            return Response({'Token': str(token)})
        else:
            raise AuthenticationFailed()

    @swagger_auto_schema(
        operation_summary='Register',
        operation_description='Create user and return its authentication token',
        request_body=UserCreateUpdateSerializer,
        responses={
            200: 'User successfully created and authenticated',
            400: 'Bad request',
        }
    )
    def post(self, request):
        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'Token': str(token)})
