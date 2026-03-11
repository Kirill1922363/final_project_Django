from django.contrib.auth.models import User
from django.db import models

from store.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Очікує обробки"),
        ("processing", "В обробці"),
        ("shipped", "Відправлено"),
        ("delivered", "Доставлено"),
        ("cancelled", "Скасовано"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    first_name = models.CharField("Імя", max_length=100)
    last_name = models.CharField("Прізвище", max_length=100)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=20)
    address = models.TextField("Адрес доставки")
    city = models.CharField("Місто", max_length=100)
    postal_code = models.CharField("Почтовий індекс", max_length=20)
    created = models.DateTimeField("Створено", auto_now_add=True)
    updated = models.DateTimeField("Оновлено", auto_now=True)
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    comment = models.TextField("Комментарій к заказу", blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Закази"
        ordering = ["-created"]

    def __str__(self):
        return f"Заказ #{self.id} — {self.user.get_full_name() or self.user.username}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Кількість", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def get_cost(self):
        return self.price * self.quantity
