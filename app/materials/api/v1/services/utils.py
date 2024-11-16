from materials.models import Material


def calculate_total(category) -> int:
    materials = Material.objects.filter(category=category).select_related('category')
    total = sum(material.price for material in materials)
    for child in category.children.all():
        total += calculate_total(child)
    return total
