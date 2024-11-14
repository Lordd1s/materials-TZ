from django.db import transaction
from materials.api.v1.serializers import MaterialWriteSerializer
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
        serializer = MaterialWriteSerializer(
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
