from django.db.models import Q
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action

from materials.models import Category, Material
from materials.api.v1.serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryTreeSerializer,
    CategoryWriteSerializer,
    MaterialFullSerializer,
    MaterialWriteSerializer,
    FileUploadSerializer
)
from materials.api.v1.services import xlsx, specific_queries


@extend_schema_view(
    list=extend_schema(
        summary='Список Материал',
        description='Получить список всех Материалов.',
        responses={200: MaterialFullSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary='Детали Материал',
        description='Получить детали конкретного Материала по его идентификатору.',
        responses={200: MaterialFullSerializer()},
    ),
    create=extend_schema(
        summary='Создать Материал',
        description='Создает новый Материал если Категория самая дочерняя',
        responses={201: MaterialWriteSerializer()},
    ),
    update=extend_schema(
        summary='Обновить Материал',
        description='Обновить информацию о существующем Материале.',
        responses={200: MaterialWriteSerializer()},
    ),
    partial_update=extend_schema(
        summary='Частичное обновление Материала',
        description='Частично обновить информацию о существующем Материале.',
        responses={200: MaterialWriteSerializer()},
    ),
    destroy=extend_schema(
        summary='Удалить Материал',
        description='Удалить существующий Материал.',
        responses={204: None},
    ),
)
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.select_related('category')
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return MaterialWriteSerializer
        return MaterialFullSerializer

    def create(self, request, *args, **kwargs):
        subcategory_id = request.data.get('subcategory_id')
        category = Category.objects.filter(
            Q(id=subcategory_id)
            &
            ~Q(children__isnull=False)
        ).first()
        if not category:
            return Response(
                {'error': 'Invalid subcategory or not a leaf category.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()
        data.pop('subcategory_id')
        Material.objects.create(
            **data,
            category=category
        )

        return Response(
            {'msg': 'Successfully created'},
            status=status.HTTP_201_CREATED
        )


class CreateMaterialFromXLSX(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        responses={
            201: 'Datas uploaded and writed to DB successfully'
        },
        summary='С xlsx файла читает и записывает в БД',
        description='ВАЖНО! Файл должен быть структурирован правильно! name, article, price, category_name'
    )
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            xlsx_data = xlsx.get_datas_from_xlsx(file, sheet_page=0)
            specific_queries.create_records(xlsx_data)
            return Response(
                {'msg': 'Datas uploaded and writed to DB successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary='Список Категории',
        description='Получить список всех Категориев.',
        responses={200: MaterialFullSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary='Детали Материал',
        description='Получить детали конкретного Категория по его идентификатору.',
        responses={200: MaterialFullSerializer()},
    ),
    create=extend_schema(
        summary='Создать Категорию',
        description='Создать новую Категорию.',
        responses={201: MaterialWriteSerializer()},
    ),
    update=extend_schema(
        summary='Обновить Категорию',
        description='Обновить информацию о существующем Категории.',
        responses={200: MaterialWriteSerializer()},
    ),
    partial_update=extend_schema(
        summary='Частичное обновление Категория',
        description='Частично обновить информацию о существующем Категории.',
        responses={200: MaterialWriteSerializer()},
    ),
    destroy=extend_schema(
        summary='Удалить Категорию',
        description='Удалить существующую Категорию.',
        responses={204: None},
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CategoryWriteSerializer
        return CategorySerializer

    @extend_schema(
        responses={
            200: CategoryTreeSerializer
        },
        summary='Список категории (tree)',
        description='Выводит список категории в виде деревьев'

    )
    @action(detail=False, methods=['get'], url_path='tree')
    def tree(self, request):
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: CategoryListSerializer
        },
        summary='Список категории',
        description='Выводит только имя'
    )
    @action(detail=False, methods=['get'], url_path='list')
    def list_categories(self, request):
        category = Category.objects.all()
        serializer = CategoryListSerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
