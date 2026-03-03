from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'city', 'status', 'created', 'get_total_cost']
    list_filter = ['status', 'created']
    list_editable = ['status']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    inlines = [OrderItemInline]

    def get_total_cost(self, obj):
        return f'{obj.get_total_cost()} грн'
    get_total_cost.short_description = 'Сумма'
