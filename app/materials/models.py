from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Категория')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name} added'


class Material(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название материала')
    category = models.ForeignKey(
        to=Category,
        on_delete=models.PROTECT,
        verbose_name='Категория')
    article = models.IntegerField(verbose_name='Код материала')
    price = models.IntegerField(verbose_name='Стоимость материала')


    class Meta:
        ordering = ('price', 'name')
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

    def __str__(self):
        return f'Добавлен материал: {self.name}'
