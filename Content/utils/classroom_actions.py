from functools import wraps

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from Content.constants import CLASSROOM_ALLOWED_ACTIONS
from Content.models import AccessGroup
from Users.models import AccessGroupUserRelation, User


def is_user_in_classroom(user, classroom):
    queryset = AccessGroupUserRelation.objects.filter(
        user=user,
        classroom=classroom,
    )
    return queryset.exists()


def user_in_classroom(func):

    @wraps(func)
    def wrapper(self, user, *args, **kwargs):
        if not is_user_in_classroom(user, self.classroom):
            return 'failed'
        return func(self, user, *args, **kwargs)


def user_not_in_classroom(func):

    @wraps(func)
    def wrapper(self, user, *args, **kwargs):
        if is_user_in_classroom(user, self.classroom):
            return 'failed'
        return func(self, user, *args, **kwargs)


def check_role(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if func.__name__ in self.allowed_actions:
            return 'failed'
        return func(self, *args, **kwargs)


class ActionDispatcher:
    def __init__(self, classroom, role):
        self.allowed_actions = CLASSROOM_ALLOWED_ACTIONS[role]
        self.classroom = classroom

    @check_role
    @user_not_in_classroom
    def add(self, user):
        access_group = AccessGroupUserRelation.objects.create(
            user=user, role='classroom_student', classroom=self.classroom
        )
        return 'success'

    @check_role
    @user_in_classroom
    def remove(self, user):
        if not user:
            return 'failed'
        access_group = AccessGroupUserRelation.objects.delete()
        return 'success'

    @check_role
    @user_in_classroom
    def set_role(self, user, role):
        if role == 'classroom_owner':
            return 'failed'
        queryset = AccessGroupUserRelation.objects.filter(
            user=user, classroom=self.classroom
        )
        queryset.update(role=role)
        return 'success'

    def dispatch(self, action, user):
        action = action['action']

        if action == 'add':
            result = self.add(user)
        elif action == 'remove':
            result = self.remove(user)
        elif action == 'set_role':
            result = self.set_role(user, action['role'])
        else:
            return 'failed'

        return result


def get_and_validate_classroom(user, id):
    """Classroom object and user's role"""

    classroom = get_object_or_404(AccessGroup, id=id)
    if classroom.type != 'classroom':
        raise PermissionDenied(
            detail='Provided id refers to access group, but not classroom'
        )
    relation = AccessGroupUserRelation.objects.filter(user=user, classroom=classroom)
    if not relation.exists():
        raise PermissionDenied(detail='User is not in classroom')

    return classroom, relation.first().role