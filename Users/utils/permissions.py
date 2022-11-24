import datetime
from rest_framework import permissions
from Content.models import AccessGroup
from Users.models import AccessGroupUserRelation
from django.shortcuts import get_object_or_404
from Users.serializers import AccessGroupUserRelationSerializer
from Users.constants import ACCESS_GROUPS


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_teacher)


class IsTeacherOrReadonly(IsTeacher):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super(IsTeacher, self).has_permission(request, view)


def check_access(group, user):
    access_group = get_object_or_404(AccessGroup, name=group)
    access_relations = AccessGroupUserRelation.objects.filter(
        user=user,
        access_group=access_group
    )
    for access_relation in access_relations:
        serialize = AccessGroupUserRelationSerializer(access_relation).data
        if serialize['expires_at'] is None:
            return True
        try:
            new_expire = serialize['expires_at'].split('.')[0] + 'Z'
            string_as_date = datetime.datetime.strptime(new_expire, '%Y-%m-%dT%H:%M:%SZ')
        except:
            string_as_date = datetime.datetime.strptime(serialize['expires_at'], '%Y-%m-%dT%H:%M:%SZ')
        if string_as_date > datetime.datetime.now():  # + datetime.timedelta(hours=2):
            return True

    return False  # update_user_access_group_by_subscriptions_payments(user, access_group)


class IsTester(permissions.BasePermission):
    def has_permission(self, request, view):
        group = ACCESS_GROUPS.LIFE_HACK_MAGIC_NUMBERS
        return check_access(group, request.user)


class IsCards(permissions.BasePermission):
    def has_permission(self, request, view):
        group = ACCESS_GROUPS.LIFE_HACK_CARDS
        return check_access(group, request.user)


class IsContent(permissions.BasePermission):
    def has_permission(self, request, view):
        group = ACCESS_GROUPS.CONTENT
        return check_access(group, request.user)


class IsLifeHackDocuments(permissions.BasePermission):
    def has_permission(self, request, view):
        group = ACCESS_GROUPS.LIFE_HACK_DOCUMENTS
        return check_access(group, request.user)


def check_has_content_access(user):
    return check_access(ACCESS_GROUPS.CONTENT, user)


def check_has_life_hack_magic_numbers_access(user):
    return check_access(ACCESS_GROUPS.LIFE_HACK_MAGIC_NUMBERS, user)


def check_has_life_hack_cards_access(user):
    return check_access(ACCESS_GROUPS.LIFE_HACK_CARDS, user)


def check_has_life_hack_documents_access(user):
    return check_access(ACCESS_GROUPS.LIFE_HACK_DOCUMENTS, user)
