from django.db import transaction
from django.db.models import Q
from materials.api.v1.serializers import MaterialFromXLSXSerializer
from materials.models import Material, Category
from rest_framework.exceptions import ValidationError


def create_records(data: list[tuple], batch_size: int | None = None):
    """
    Создает записи с xlsx файла

    :param data: Принимает Список с материалами
    :param batch_size: Это нужно для bulk_create операции! По умоланию None
    :return: 'None'
    """
    pre_materials = []
    for item in data:
        serializer = MaterialFromXLSXSerializer(
            data={
                'name': item[0],
                'article': int(item[1]),
                'price': int(item[2]),
            }
        )
        if serializer.is_valid():
            category = Category.objects.filter(name=item[3]).first()
            if category:
                pre_materials.append(
                    Material(**serializer.validated_data, category=category)
                )
            else:
                raise ValidationError(f'Category {item[3]}: not found!')
        else:
            raise ValidationError(f'Validation failed for {item}: {serializer.errors}')
    if pre_materials:
        with transaction.atomic():
            Material.objects.bulk_create(pre_materials, batch_size=batch_size)


def get_subcategory(subcategory_id: int) -> Category | None:
    """
    Возвращает самую дочернюю категорию

    :param subcategory_id: Идентификатор дочерней категории
    :return: объект Category
    """
    category  = Category.objects.filter(
            Q(id=subcategory_id)
            &
            ~Q(children__isnull=False)
        ).first()

    return category