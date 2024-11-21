from rest_framework import serializers

from materials.models import Category, Material
from materials.api.v1.services.utils import calculate_total


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class CategoryListSerializer(serializers.Serializer):
    name = serializers.CharField()

    def to_representation(self, instance):
        return instance.name


class CategoryWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'parent')


class MaterialFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = '__all__'


class MaterialCreateSerializer(serializers.ModelSerializer):
    subcategory = serializers.IntegerField()

    class Meta:
        model = Material
        fields = ('name', 'article', 'price', 'subcategory')


class MaterialPutUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    article = serializers.IntegerField()
    price = serializers.IntegerField()

    class Meta:
        model = Material
        fields = ('name', 'article', 'price')


class MaterialPatchUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    article = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)

    class Meta:
        model = Material
        fields = ('name', 'article', 'price')


class MaterialSerializerForTree(MaterialFullSerializer):
    pass


class CategoryTreeSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'subcategories', 'materials', 'total_sum')

    def get_subcategories(self, instance: Category) -> dict | None:
        subcategories = Category.objects.filter(parent=instance)
        serializer = CategoryTreeSerializer(subcategories, many=True)
        return serializer.data

    def get_materials(self, instance: Category) -> dict | None:
        materials = Material.objects.filter(category=instance).select_related('category')
        serializer = MaterialSerializerForTree(materials, many=True)
        return serializer.data

    def get_total_sum(self, instance: Category) -> int:
        result = calculate_total(instance)
        return result


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith('.xlsx'):
            raise serializers.ValidationError('Only .xlsx files are allowed')
        return value