from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("Назва", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    image = models.ImageField("Изображение", upload_to="categories/", blank=True)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_list_by_category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категорія",
    )
    name = models.CharField("Назва", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    description = models.TextField("Опис", blank=True)
    price = models.DecimalField("Ціна", max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        "Старая цена", max_digits=10, decimal_places=2, blank=True, null=True
    )
    image = models.ImageField("Изображение", upload_to="products/", blank=True)
    stock = models.PositiveIntegerField("Залишок на складі", default=0)
    available = models.BooleanField("Доступний", default=True)
    featured = models.BooleanField("На головній", default=False)
    created = models.DateTimeField("Створено", auto_now_add=True)
    updated = models.DateTimeField("Оновлено", auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ["-created"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])

    def get_discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return None
