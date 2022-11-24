from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from Users.utils.permissions import IsTeacherOrReadonly
from Users.models import AccessGroupUserRelation, User
from Content.utils import (
    get_and_validate_classroom,
    generate_invite_code,
)

from Content.utils.classroom_actions import ActionDispatcher
from Content.models import (
    AccessGroup,
)
from Content.serializers import (
    ClassroomCreateSerializer,
    ClassroomEnrollSerializer,
    ClassroomSerializer,
    ClassroomUpdateSerializer,
)


class ClassroomView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsTeacherOrReadonly]

    @swagger_auto_schema(
        operation_summary='Get classroom',
        operation_description='Get classroom and users in classroom with their roles',
        responses={
            200: ClassroomSerializer,
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request, classroom_id=None):
        """List classrooms or Retrieve classroom if specified"""
        if classroom_id is not None:
            classroom, role = get_and_validate_classroom(request.user, id=classroom_id)
            relations = AccessGroupUserRelation.objects.filter(access_group=classroom_id)
            data = ClassroomSerializer(classroom).data
            data.users = list(
                relations.values('role', 'user__username')
            )
            return data
        else:
            relations = AccessGroupUserRelation.objects.filter(user=request.user)
            return list(
                relations.values('role', 'access_group__name', 'access_group__type')
            )

    @swagger_auto_schema(
        operation_summary='Create classroom',
        operation_description='Create classroom',
        request_body=ClassroomCreateSerializer,
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def post(self, request):
        """Create classroom"""
        serializer = ClassroomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        classroom = AccessGroup.objects.create(
            name=serializer.validated_data,
            type='classroom',
            invite_code=generate_invite_code(),
        )
        AccessGroupUserRelation.objects.create(
            user=request.user,
            access_group=classroom,
            type='classroom',
        )
        return ClassroomSerializer(classroom).data

    @swagger_auto_schema(
        operation_summary='Update classroom',
        operation_description=(
                'Updated classroom\n'
                'Available actions:\n'
                '<add>  Add user [username] (role is set to student)\n'
                '<remove>  Remove user [username]\n'
                '<set_role>  Set user role [username, role]\n'
        ),
        request_body=ClassroomUpdateSerializer,
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
            404: 'Classroom not found',
        }
    )
    def patch(self, request, classroom_id):
        """Update classroom"""
        classroom, role = get_and_validate_classroom(request.user, id=classroom_id)
        serializer = ClassroomUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Rename if new name provided
        new_name = data.get('new_name', None)
        if new_name is not None:
            classroom.name = new_name
            classroom.save()

        dispatcher = ActionDispatcher(classroom, role)
        actions = data.get('actions', [])
        for action in actions:
            user_queryset = User.objects.filter(username=action['username'])
            if not user_queryset.exists():
                action['result'] = 'failed'
                continue
            user = user_queryset.first()
            action['result'] = dispatcher.dispatch(action, user)

        return data


class ClassroomEnrollView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Join classroom',
        operation_description='Join classroom with invite code',
        query_serializer=ClassroomEnrollSerializer,
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
            404: 'Classroom not found',
        }
    )
    def post(self, request):
        serializer = ClassroomEnrollSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite_code = serializer.validated_data['invite_code']

        classroom = get_object_or_404(AccessGroup, invite_code=invite_code)
        AccessGroup.objects.get_or_create(
            user=request.user,
            classroom=classroom,
            defaults={'role': 'classroom_student'}
        )

        return Response('OK')
