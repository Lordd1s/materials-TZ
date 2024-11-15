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


class MaterialNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = ('name', )


class MaterialFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = '__all__'


class MaterialWriteSerializer(serializers.ModelSerializer):
    subcategory_id = serializers.IntegerField()

    class Meta:
        model = Material
        fields = ('name', 'article', 'price', 'subcategory_id')


class MaterialSerializerForTree(MaterialFullSerializer):
    pass


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith('.xlsx'):
            raise serializers.ValidationError('Only .xlsx files are allowed')
        return value


class CategoryTreeSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'subcategories', 'materials', 'total_sum')

    def get_subcategories(self, instance: Category):
        subcategories = Category.objects.filter(parent=instance)
        serializer = CategoryTreeSerializer(subcategories, many=True)
        return serializer.data

    def get_materials(self, instance: Category):
        materials = Material.objects.filter(category=instance).select_related('category')
        serializer = MaterialSerializerForTree(materials, many=True)
        return serializer.data

    def get_total_sum(self, instance: Category):
        result = calculate_total(instance)
        return result
