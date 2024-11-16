from django.db.models import Q
from materials.models import Material, Category


def create_material(pre_material_data: dict, category_id: int) -> Material:
    category = Category.objects.filter(
        Q(id=category_id)
        &
        ~Q(children__isnull=False)
    ).first()
    if not category:
        raise Exception('Invalid subcategory or not a leaf category.')
    material_data = pre_material_data.copy()
    material_data.pop('subcategory')
    material = Material.objects.create(
        **material_data,
        category=category
    )
    return material


def create_category(name: str, parent_id: int=None) -> Category:
    category = Category.objects.create(
        name=name,
        parent=parent_id
    )

    return category
