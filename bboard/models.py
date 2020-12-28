from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models


def validate_min_value(val):
    if val < 0:
        raise ValidationError('Число %(value)s меньше 0, исправьте это', params={'value': val})


def validate_proper_string_name(s, banned_chars=(' ', ',', '.', ':', ';'), numbers=(1, 2, 3, 4, 5, 6, 7, 8, 9, 0)):
    for i in s:
        if i in numbers or i in banned_chars:
            raise ValidationError('В данном поле должны быть только буквы, эти символы также недопустимы: %s' % ', '
                                  .join(banned_chars))


class RubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def order_by_bb_count(self):
        return super().get_queryset.annotate(cnt=models.Count('bb')).order_by('-cnt')


class Bb(models.Model):
    KINDS = (
        ('Покупка', 'Покупка'),
        ('Продажа', 'Продажа'),
        ('Обмен', 'Обмен'),
        (None, 'Продажа/Обмен'),
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                verbose_name='Создатель объявления')
    kind = models.CharField(max_length=8, choices=KINDS, default='Продажа', verbose_name='Цель объявления')
    title = models.CharField(max_length=20, verbose_name='Товар')
    content = models.TextField(null=True, blank=True, verbose_name='Описание')
    price = models.FloatField(null=True, blank=True, verbose_name="Цена", validators=[validate_min_value])
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.CASCADE, verbose_name='Рубрика')
    image = models.ImageField(null=True, upload_to='archive',
                              validators=[validators.FileExtensionValidator(allowed_extensions=('gif', 'png', 'jpg'))],
                              error_messages={'invalid_extension': 'Выбранный тип файла не поддерживается'},
                              verbose_name='Фото товара')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-published']


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name='Название', unique=True,
                            validators=[validate_proper_string_name])

    objects = RubricManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'
        ordering = ['name']


class Comment(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE)
    author_name = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                    verbose_name='Имя комментатора')
    comm_text = models.TextField(verbose_name='Комментарий')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    def __str__(self):
        return self.author_name

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['-published']


class Img(models.Model):
    img = models.ImageField(verbose_name='Изображение', upload_to='archive',
                            validators=[validators.FileExtensionValidator(allowed_extensions=('gif', 'png', 'jpg'))],
                            error_messages={'invalid_extension': 'Выбранный тип файла не поддерживается'})
    desc = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return self.desc
