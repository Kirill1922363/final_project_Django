from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Фильтрация
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort = request.GET.get("sort", "-created")
    query = request.GET.get("q", "")

    if query:
        products = products.filter(name__icontains=query)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    allowed_sorts = ["price", "-price", "-created", "name"]
    if sort in allowed_sorts:
        products = products.order_by(sort)

    featured = Product.objects.filter(available=True, featured=True)[:6]

    return render(
        request,
        "store/product_list.html",
        {
            "categories": categories,
            "products": products,
            "category": category,
            "featured": featured,
            "sort": sort,
            "query": query,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related = Product.objects.filter(category=product.category, available=True).exclude(
        id=product.id
    )[:4]
    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "related": related,
        },
    )
