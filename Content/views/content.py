from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from math import ceil

from APIBackendService.views import AppAPIView, BaseAppReadOnlyModelViewSet
from Content.models import ContentIndexRelationship, Product
from Content.serializers import ContentWikiItemSerializer, ContentWikiPreviewSerializer, TrainerBlockSerializer, \
    NamesSearchSerializer
from Content.service import content_total_update, update_content_indexes_relations
from Users.utils.permissions import check_has_content_access
from Content.utils import (
    get_video_info
)

from Content.constants import (
    QUESTIONS,
)

from Statistics.models import ActivityLog

from Content.utils.wiki_content import get_code_from_table, get_wiki_content_table, \
    check_table_in_wiki_tables, get_content_table

from Services.service.search import (
    search_full_content_objects_in_table,
    search_content_object_names_in_table,
    add_all_data_from_tables_to_search_indexes,
)

from Content.service.wiki_content import (
    get_preview_related_objects_for_item
)


class PaginationWikiContent(LimitOffsetPagination):
    # page_size = 20
    default_limit = 20
    max_limit = 20

    def get_next_offset(self):
        if self.offset + self.limit >= self.count:
            return None
        return self.offset + self.limit

    def get_previous_offset(self):
        if self.offset - self.limit < 0:
            return None

        return self.offset - self.limit

    def get_paginated_response(self, data):
        pages = ceil(self.count / self.limit)
        return Response({
            'links': {
                'next': {
                    'link': self.get_next_link(),
                    'offset': self.get_next_offset(),
                },
                'previous': {
                    'link': self.get_previous_link(),
                    'offset': self.get_previous_offset(),
                },
            },
            'limit': self.limit,
            'offset': self.offset,
            'count': self.count,
            'pages': pages,
            # 'limit': self.page_size,
            # 'page': self.page.number,
            'data': data
        })


class PaginationWikiRelatedItems(PaginationWikiContent):
    default_limit = 10
    max_limit = 10


# http://localhost:8000/api/content/content/add/
class AddContentItems(AppAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_summary='Update content [admins only]',
        operation_description='Update content tables [admins only]',
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def post(self, request):
        return Response(content_total_update(request.data))
        # return Response(add_content_items_to_tables(request.data))


class AddDataToSearchView(AppAPIView):
    """
    One-time view for adding all information to search index
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        add_all_data_from_tables_to_search_indexes()
        return Response(200)


# http://localhost:8000/api/content/search/names/
class ContentFastSearchNamesView(AppAPIView):
    """
    Fast-search names
    """

    @swagger_auto_schema(
        operation_summary='Search names',
        operation_description='Search names from content tables',
        # manual_parameters=[
        #     openapi.Parameter('q', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        # ],
        query_serializer=NamesSearchSerializer(),
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request, table=None):
        q = request.GET.get("q", "")
        # table = request.GET.get("table")

        return Response(search_content_object_names_in_table(
            q, table
        ))


# http://localhost:8000/api/content/search/all/
class ContentFastSearchFullObjectsView(AppAPIView):
    """
    Fast-search content objects
    """

    @swagger_auto_schema(
        operation_summary='Search content',
        operation_description='Search for full objects from content tables',
        manual_parameters=[
            openapi.Parameter('q', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('offset', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request, table=None):
        q = request.GET.get("q", "")
        # table = request.GET.get("table")
        offset = int(request.GET.get("offset", 0))

        return Response(search_full_content_objects_in_table(
            request.user, q, table, offset
        ))


class UpdateContentRelations(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        update_content_indexes_relations(request.data)
        return Response(200)


class ContentWikiTemplateViewSet(BaseAppReadOnlyModelViewSet):
    """
    Template class for content wiki items
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_url_kwarg = 'index'
    lookup_field = 'index'

    preview_request = None

    def get_serializer_context(self):
        return {
            "access": check_has_content_access(self.request.user),
            "table": self.kwargs.get("table", None),
        }

    def get_queryset(self):
        table = self.kwargs["table"]
        content_model = get_wiki_content_table(table)
        return content_model.objects.all()

    def save_list_activity(self, request):
        table = self.kwargs['table']
        ActivityLog.objects.create(user=request.user, activity=f"C_LIST {table}")

    def save_retrieve_activity(self, request):
        user = request.user
        activity_point = "1" if self.preview_request else "0"
        table = self.kwargs['table']
        index = self.kwargs['index']
        table_code = get_code_from_table(table)
        try:
            ActivityLog.objects.create(user=user, activity=f"C_CON{activity_point} {table}")
            ActivityLog.objects.create(user=user, activity=f"C{activity_point} {table_code} {index}")
        except:
            pass

    def save_activity(self, request):
        # print("Action:", self.action)
        if self.action == 'list':
            self.save_list_activity(request)
        elif self.action == 'retrieve':
            self.save_retrieve_activity(request)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        # SAVE ACTIVITY ###########
        self.save_activity(request)

        return response

    def structure(self, request, *args, **kwargs):
        # try:
        # if True:
        try:
            limit = self.pagination_class.default_limit
        except:
            limit = 20
        indexes = []
        queryset = self.get_queryset()
        count = queryset.count()
        amount = ceil(count / limit)
        for i in range(amount):
            indexes.append(i * limit)
            indexes.append(min((i + 1) * limit - 1, count - 1))
        from_queryset = queryset[::limit]
        to_queryset = queryset[limit - 1::limit]
        # items = queryset[indexes]
        config = {
            'pages_amount': amount,
            'limit': limit,
            'count': count,
            'pages': [],
        }
        from_queryset_count = len(from_queryset)
        to_queryset_count = len(to_queryset)
        for i, i1 in enumerate(from_queryset):
            config["pages"].append({
                'from': {
                    'name': i1.name,
                },
                'to': {
                    'name': '',  # i2.name,
                },
                'amount': indexes[i * 2 + 1] - indexes[i * 2] + 1,
                'offset': i * limit,
            })
        for i, i2 in enumerate(to_queryset):
            config["pages"][i]['to']['name'] = i2.name
        if from_queryset_count > to_queryset_count:
            config["pages"][-1]['to']['name'] = queryset.last().name
        # except Exception as e:
        #     print("Error:", e)
        return Response(config)


class ContentWikiPreviewViewSet(ContentWikiTemplateViewSet):
    """
    Preview for content wiki items

    For test:
    1. Retrieve: http://localhost:8000/api/content/wiki/item/preview/PERSONS/100000
    2. List: http://localhost:8000/api/content/wiki/item/preview/PERSONS/
    3. Structure: http://localhost:8000/api/content/wiki/item/preview/structure/PERSONS/
    """

    pagination_class = PaginationWikiContent
    serializer_class = ContentWikiPreviewSerializer
    preview_request = True


class ContentWikiFullView(ContentWikiTemplateViewSet):
    """
    Preview for content wiki items

    For test:
    1. Retrieve: http://localhost:8000/api/content/wiki/item/full/PERSONS/100000
    """

    serializer_class = ContentWikiItemSerializer
    preview_request = False

    def retrieve(self, request, *args, **kwargs):

        # try:
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        table = self.kwargs['table']
        index = self.kwargs['index']

        result = {"item": serializer.data}
        # except Exception as e:
        #     print("Err", e)
        # try:
        result.update(get_preview_related_objects_for_item(
            table, index, self.get_serializer_context()["access"]
        ))
        # except Exception as e:
        #     print("Err", e)

        return Response(result)


class ContentWikiRelatedItemsView(ContentWikiTemplateViewSet):
    """
    Preview for content wiki items

    For test:
    1. Retrieve: http://localhost:8000/api/content/wiki/item/related/PERSONS/1000/?table_relation=PERSONS
    """

    pagination_class = PaginationWikiRelatedItems
    preview_request = True

    def get_serializer_context(self):
        super_context = super().get_serializer_context()
        super_context.update({
            "table": self.request.query_params.get('table_relation')
        })
        return super_context

    def save_list_activity(self, request):
        table = self.kwargs['table']
        ActivityLog.objects.create(user=request.user, activity=f"C_REL {table}")

    def get_serializer_class(self):
        # print("Serializer")
        table_relation = self.request.query_params.get('table_relation')
        if table_relation == QUESTIONS:
            return TrainerBlockSerializer
        return ContentWikiPreviewSerializer

    def get_queryset(self):
        # print(get_object_or_404(Product, id=1).__dict__)
        table = self.kwargs["table"]
        index = self.kwargs["index"]
        table_relation = self.request.query_params.get("table_relation")

        check_table_in_wiki_tables(table)
        # check_table_in_content_tables(table_relation)
        content_model = get_content_table(table_relation)

        code = get_code_from_table(table)  # table[:2]
        second_code = get_code_from_table(table_relation)  # table_relation[:2]
        relations = ContentIndexRelationship.objects.filter(
            first_code=code,
            first_index=index,
            second_code=second_code,
        )
        second_codes = list(map(lambda x: x.second_index, relations))
        # print("SECOND CODES:", second_codes)
        return content_model.objects.filter(index__in=second_codes)


class ContentVideoGet(AppAPIView):

    @swagger_auto_schema(
        operation_summary='Video info',
        operation_description='Video info get',
        manual_parameters=[
            openapi.Parameter('index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description="Video index"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request):
        index = int(request.GET.get('index', -1))
        if index < 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Нет информации о видео'})

        user = request.user
        # user = User.objects.filter(username='vk__209636450').first()

        access = check_has_content_access(user)

        try:
            info = get_video_info(index, access)
            return Response({
                "access": access,
                "info": info,
            })
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Неверный индекс видео'})


class ContentVideoAccess(AppAPIView):

    @swagger_auto_schema(
        operation_summary='Video access',
        operation_description='Video access checker',
        manual_parameters=[
            openapi.Parameter('index', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description="Video index"),
        ],
        responses={
            200: 'OK',
            400: 'Bad request',
            403: 'Not permitted',
        }
    )
    def get(self, request):

        index = int(request.GET.get('index', -1))
        if index < 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Нет информации о видео'})

        access = check_has_content_access(request.user)

        try:
            if access:
                info = get_video_info(index, access)
                return Response({
                    "access": True,
                    "info": info,
                })
            else:
                return Response(status=status.HTTP_403_FORBIDDEN, data={
                    'error': 'Нет доступа',
                    'access': 'content',
                })
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Неверный индекс видео'})
