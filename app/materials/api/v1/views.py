from drf_spectacular.utils import extend_schema_view, extend_schema, extend_schema_field
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
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
    MaterialCreateSerializer,
    MaterialPutUpdateSerializer,
    MaterialPatchUpdateSerializer,
    FileUploadSerializer
)
from materials.api.v1.services import xlsx, specific_queries


@extend_schema_view(
    list=extend_schema(
        summary='Список Материалов',
        description='Получить список всех Материалов.',
        responses={200: MaterialFullSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary='Детали Материала',
        description='Получить детали конкретного Материала по его идентификатору.',
        responses={200: MaterialFullSerializer},
    ),
    create=extend_schema(
        summary='Создание Материала',
        responses={201: MaterialCreateSerializer},
    ),
    update=extend_schema(
        summary='Обновление Материала',
        description='Обновить информацию о существующем Материале.',
        responses={200: MaterialPutUpdateSerializer},
    ),
    partial_update=extend_schema(
        summary='Частичное обновление Материала',
        description='Частично обновить информацию о существующем Материале.',
        responses={200: MaterialPatchUpdateSerializer},
    ),
    destroy=extend_schema(
        summary='Удаление Материала',
        responses={204: None},
    )
)
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.select_related('category')

    def get_serializer_class(self):
        match self.action:
            case 'create':
                return MaterialCreateSerializer
            case 'update':
                return MaterialPutUpdateSerializer
            case 'partial_update':
                return MaterialPatchUpdateSerializer
            case _:
                return MaterialFullSerializer

    def create(self, request, *args, **kwargs):
        subcategory = request.data['subcategory']
        category = specific_queries.get_subcategory(subcategory)

        if not category:
            raise NotFound('Category not found or not leaf category')

        serializer = MaterialCreateSerializer(data=request.data)
        if serializer.is_valid():
            pre_material = serializer.validated_data.copy()
            pre_material.pop('subcategory')
            material = Material.objects.create(
                **pre_material,
                category=category
            )
            return Response(MaterialFullSerializer(material).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            201: {'msg': 'Datas uploaded and writed to DB successfully'}
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
        responses={200: CategorySerializer},
    ),
    retrieve=extend_schema(
        summary='Детали Категории',
        description='Получить детали конкретного Категория по его идентификатору.',
        responses={200: CategorySerializer},
    ),
    create=extend_schema(
        summary='Создать Категорию',
        description='Создать новую Категорию.',
        responses={201: CategoryWriteSerializer},
    ),
    update=extend_schema(
        summary='Обновить Категорию',
        description='Обновить информацию о существующем Категории.',
        responses={200: CategoryWriteSerializer},
    ),
    partial_update=extend_schema(
        summary='Частичное обновление Категория',
        description='Частично обновить информацию о существующем Категории.',
        responses={200: CategoryWriteSerializer},
    ),
    destroy=extend_schema(
        summary='Удалить Категорию',
        description='Удалить существующую Категорию.',
        responses={204: None},
    )
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CategoryWriteSerializer
        return CategorySerializer

    @extend_schema(
        summary='Вывод категорий плоским списком',
        description='Возвращает категории плоским списком.',
        responses={200: CategoryListSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='flat_list')
    def list_categories(self, request):
        category = Category.objects.all()
        serializer = CategoryListSerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema_field(CategoryTreeSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='tree')
    def tree(self, request):
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

