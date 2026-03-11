from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Profile
from cart.cart import Cart
from orders.models import Order, OrderItem
from store.models import Category, Product

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────


def make_category(name="Laptops", slug="laptops"):
    return Category.objects.create(name=name, slug=slug)


def make_product(
    category,
    name="Dell XPS 15",
    slug="dell-xps-15",
    price="84999.00",
    old_price=None,
    stock=10,
    available=True,
    featured=False,
):
    return Product.objects.create(
        category=category,
        name=name,
        slug=slug,
        description="Great laptop",
        price=Decimal(price),
        old_price=Decimal(old_price) if old_price else None,
        stock=stock,
        available=available,
        featured=featured,
    )


def make_user(username="testuser", password="TestPass123!"):
    return User.objects.create_user(
        username=username,
        password=password,
        email=f"{username}@example.com",
        first_name="John",
        last_name="Doe",
    )


# ═════════════════════════════════════════════
#  STORE — Models
# ═════════════════════════════════════════════


class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = make_category()

    def test_str(self):
        self.assertEqual(str(self.category), "Laptops")

    def test_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertEqual(
            url, reverse("store:product_list_by_category", args=["laptops"])
        )

    def test_ordering_by_name(self):
        make_category("Accessories", "accessories")
        make_category("Smartphones", "smartphones")
        names = list(Category.objects.values_list("name", flat=True))
        self.assertEqual(names, sorted(names))


class ProductModelTest(TestCase):

    def setUp(self):
        self.cat = make_category()
        self.product = make_product(self.cat)

    def test_str(self):
        self.assertEqual(str(self.product), "Dell XPS 15")

    def test_get_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertEqual(url, reverse("store:product_detail", args=["dell-xps-15"]))

    def test_get_discount_percent_with_old_price(self):
        p = make_product(
            self.cat, name="Sale", slug="sale", price="80000", old_price="100000"
        )
        self.assertEqual(p.get_discount_percent(), 20)

    def test_get_discount_percent_without_old_price(self):
        self.assertIsNone(self.product.get_discount_percent())

    def test_get_discount_percent_old_less_than_price(self):
        """No discount when old_price <= price (data anomaly guard)."""
        p = make_product(
            self.cat, name="NoSale", slug="no-sale", price="100000", old_price="80000"
        )
        self.assertIsNone(p.get_discount_percent())

    def test_default_stock_zero(self):
        p = Product.objects.create(
            category=self.cat,
            name="Empty",
            slug="empty",
            price=Decimal("100.00"),
        )
        self.assertEqual(p.stock, 0)

    def test_available_default_true(self):
        self.assertTrue(self.product.available)


# ═════════════════════════════════════════════
#  STORE — Views
# ═════════════════════════════════════════════


class ProductListViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category()
        self.cat2 = make_category("Smartphones", "smartphones")
        self.p1 = make_product(self.cat, featured=True)
        self.p2 = make_product(
            self.cat2, name="iPhone 15", slug="iphone-15", price="54999"
        )
        self.p_hidden = make_product(
            self.cat, name="Hidden", slug="hidden", available=False
        )

    def test_status_ok(self):
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("store:product_list"))
        self.assertTemplateUsed(response, "store/product_list.html")

    def test_unavailable_product_hidden(self):
        response = self.client.get(reverse("store:product_list"))
        names = [p.name for p in response.context["products"]]
        self.assertNotIn("Hidden", names)

    def test_filter_by_category(self):
        url = reverse("store:product_list_by_category", args=["laptops"])
        response = self.client.get(url)
        names = [p.name for p in response.context["products"]]
        self.assertIn("Dell XPS 15", names)
        self.assertNotIn("iPhone 15", names)

    def test_search_by_query(self):
        response = self.client.get(reverse("store:product_list"), {"q": "iphone"})
        names = [p.name for p in response.context["products"]]
        self.assertIn("iPhone 15", names)
        self.assertNotIn("Dell XPS 15", names)

    def test_filter_by_min_price(self):
        response = self.client.get(
            reverse("store:product_list"), {"min_price": "60000"}
        )
        prices = [p.price for p in response.context["products"]]
        for price in prices:
            self.assertGreaterEqual(price, Decimal("60000"))

    def test_filter_by_max_price(self):
        response = self.client.get(
            reverse("store:product_list"), {"max_price": "60000"}
        )
        prices = [p.price for p in response.context["products"]]
        for price in prices:
            self.assertLessEqual(price, Decimal("60000"))

    def test_sort_by_price_ascending(self):
        response = self.client.get(reverse("store:product_list"), {"sort": "price"})
        prices = [p.price for p in response.context["products"]]
        self.assertEqual(prices, sorted(prices))

    def test_sort_by_price_descending(self):
        response = self.client.get(reverse("store:product_list"), {"sort": "-price"})
        prices = [p.price for p in response.context["products"]]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_featured_in_context(self):
        response = self.client.get(reverse("store:product_list"))
        featured = response.context["featured"]
        self.assertIn(self.p1, featured)


class ProductDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category()
        self.product = make_product(self.cat)
        self.related = make_product(
            self.cat, name="MacBook Pro", slug="macbook-pro", price="109999"
        )

    def test_status_ok(self):
        response = self.client.get(
            reverse("store:product_detail", args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(
            reverse("store:product_detail", args=[self.product.slug])
        )
        self.assertTemplateUsed(response, "store/product_detail.html")

    def test_404_for_unavailable(self):
        response = self.client.get(reverse("store:product_detail", args=["gone"]))
        self.assertEqual(response.status_code, 404)

    def test_related_products_in_context(self):
        response = self.client.get(
            reverse("store:product_detail", args=[self.product.slug])
        )
        related = response.context["related"]
        self.assertIn(self.related, related)
        self.assertNotIn(self.product, related)

    def test_product_in_context(self):
        response = self.client.get(
            reverse("store:product_detail", args=[self.product.slug])
        )
        self.assertEqual(response.context["product"], self.product)


# ═════════════════════════════════════════════
#  CART — Logic
# ═════════════════════════════════════════════


class CartTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.cat = make_category()
        self.p1 = make_product(self.cat)
        self.p2 = make_product(self.cat, name="MacBook", slug="macbook", price="109999")

    def _get_cart(self):
        session = self.client.session
        request = type("R", (), {"session": session})()
        return Cart(request)

    def test_add_product(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.p1.id]),
            {"quantity": 2, "override": False},
        )
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.p1.name)

    def test_add_increases_quantity(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.p1.id]),
            {"quantity": 1, "override": False},
        )
        self.client.post(
            reverse("cart:cart_add", args=[self.p1.id]),
            {"quantity": 3, "override": False},
        )
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "4")

    def test_override_quantity(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.p1.id]),
            {"quantity": 5, "override": False},
        )
        self.client.post(
            reverse("cart:cart_add", args=[self.p1.id]),
            {"quantity": 2, "override": True},
        )
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, self.p1.name)

    def test_remove_product(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.p1.id]),
            {"quantity": 1, "override": False},
        )
        self.client.post(reverse("cart:cart_remove", args=[self.p1.id]))
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertNotContains(response, self.p1.name)

    def test_cart_detail_empty(self):
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "порожній")

    def test_add_requires_post(self):
        response = self.client.get(reverse("cart:cart_add", args=[self.p1.id]))
        self.assertEqual(response.status_code, 405)

    def test_remove_requires_post(self):
        response = self.client.get(reverse("cart:cart_remove", args=[self.p1.id]))
        self.assertEqual(response.status_code, 405)

    def test_add_nonexistent_product_404(self):
        response = self.client.post(
            reverse("cart:cart_add", args=[99999]),
            {"quantity": 1, "override": False},
        )
        self.assertEqual(response.status_code, 404)

    def test_cart_total_price(self):
        """Cart total = sum(price * quantity) for all items."""
        self.client.post(
            reverse("cart:cart_add", args=[self.p1.id]),
            {"quantity": 2, "override": False},
        )
        self.client.post(
            reverse("cart:cart_add", args=[self.p2.id]),
            {"quantity": 1, "override": False},
        )
        # p1: 84999 * 2 + p2: 109999 * 1 = 279997
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "279997")


# ═════════════════════════════════════════════
#  ORDERS — Models & Views
# ═════════════════════════════════════════════


class OrderModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.cat = make_category()
        self.product = make_product(self.cat)
        self.order = Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+380991234567",
            address="123 Main St",
            city="Kyiv",
            postal_code="01001",
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal("84999.00"),
            quantity=2,
        )

    def test_order_str(self):
        self.assertIn(str(self.order.id), str(self.order))

    def test_order_item_str(self):
        self.assertIn("Dell XPS 15", str(self.item))

    def test_order_item_get_cost(self):
        self.assertEqual(self.item.get_cost(), Decimal("169998.00"))

    def test_order_get_total_cost(self):
        self.assertEqual(self.order.get_total_cost(), Decimal("169998.00"))

    def test_order_default_status(self):
        self.assertEqual(self.order.status, "pending")

    def test_order_ordering_newest_first(self):
        order2 = Order.objects.create(
            user=self.user,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="+1",
            address="456 St",
            city="Lviv",
            postal_code="79000",
        )
        orders = list(Order.objects.all())
        self.assertEqual(orders[0], order2)


class OrderViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.cat = make_category()
        self.product = make_product(self.cat)

    def _login(self):
        self.client.login(username="testuser", password="TestPass123!")

    def _add_to_cart(self):
        self.client.post(
            reverse("cart:cart_add", args=[self.product.id]),
            {"quantity": 1, "override": False},
        )

    def test_order_create_requires_login(self):
        response = self.client.get(reverse("orders:order_create"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('orders:order_create')}",
        )

    def test_order_create_empty_cart_redirects(self):
        self._login()
        response = self.client.get(reverse("orders:order_create"))
        self.assertRedirects(response, reverse("cart:cart_detail"))

    def test_order_create_get(self):
        self._login()
        self._add_to_cart()
        response = self.client.get(reverse("orders:order_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/create.html")

    def test_order_create_post_success(self):
        self._login()
        self._add_to_cart()
        response = self.client.post(
            reverse("orders:order_create"),
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+380991234567",
                "address": "123 Main St",
                "city": "Kyiv",
                "postal_code": "01001",
                "comment": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/created.html")
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)

    def test_order_create_clears_cart(self):
        self._login()
        self._add_to_cart()
        self.client.post(
            reverse("orders:order_create"),
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+380991234567",
                "address": "123 Main St",
                "city": "Kyiv",
                "postal_code": "01001",
                "comment": "",
            },
        )
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "порожній")

    def test_order_list_requires_login(self):
        response = self.client.get(reverse("orders:order_list"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('orders:order_list')}",
        )

    def test_order_list_shows_only_own_orders(self):
        self._login()
        other_user = make_user(username="other", password="OtherPass123!")
        Order.objects.create(
            user=other_user,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="+1",
            address="456 St",
            city="Lviv",
            postal_code="79000",
        )
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["orders"].count(), 0)

    def test_order_detail_requires_login(self):
        order = Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+380991234567",
            address="123 Main St",
            city="Kyiv",
            postal_code="01001",
        )
        response = self.client.get(reverse("orders:order_detail", args=[order.id]))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next="
            f"{reverse('orders:order_detail', args=[order.id])}",
        )

    def test_order_detail_not_accessible_by_other_user(self):
        order = Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+380991234567",
            address="123 Main St",
            city="Kyiv",
            postal_code="01001",
        )

        response = self.client.get(reverse("orders:order_detail", args=[order.id]))
        self.assertEqual(response.status_code, 404)


# ═════════════════════════════════════════════
#  ACCOUNTS — Models & Views
# ═════════════════════════════════════════════


class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.profile = Profile.objects.create(
            user=self.user,
            phone="+380991234567",
            city="Kyiv",
            address="123 Main St",
        )

    def test_profile_str(self):
        self.assertIn("testuser", str(self.profile))

    def test_profile_linked_to_user(self):
        self.assertEqual(self.profile.user, self.user)

    def test_profile_fields(self):
        self.assertEqual(self.profile.phone, "+380991234567")
        self.assertEqual(self.profile.city, "Kyiv")


class RegisterViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("accounts:register")

    def test_register_page_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_authenticated_redirects(self):
        make_user()
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("store:product_list"))

    def test_register_success(self):
        response = self.client.post(
            self.url,
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("store:product_list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_creates_profile(self):
        self.client.post(
            self.url,
            {
                "username": "newuser2",
                "first_name": "New",
                "last_name": "User",
                "email": "new2@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        user = User.objects.get(username="newuser2")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_invalid_password_mismatch(self):
        response = self.client.post(
            self.url,
            {
                "username": "baduser",
                "first_name": "Bad",
                "last_name": "User",
                "email": "bad@example.com",
                "password1": "StrongPass123!",
                "password2": "WrongPass456!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="baduser").exists())


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.url = reverse("accounts:login")

    def test_login_page_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_success(self):
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "password": "TestPass123!",
            },
        )
        self.assertRedirects(response, reverse("store:product_list"))

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url,
            {
                "username": "testuser",
                "password": "WrongPassword!",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("store:product_list"))


class ProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.url = reverse("accounts:profile")

    def test_profile_requires_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_profile_page_get(self):
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_update(self):
        self.client.login(username="testuser", password="TestPass123!")
        Profile.objects.get_or_create(user=self.user)
        response = self.client.post(
            self.url,
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com",
                "phone": "+380991111111",
                "city": "Lviv",
                "address": "456 Updated St",
            },
        )
        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_profile_autocreated_if_missing(self):
        """Profile view should create a Profile if it doesn't exist yet."""
        self.client.login(username="testuser", password="TestPass123!")
        self.assertFalse(Profile.objects.filter(user=self.user).exists())
        self.client.get(self.url)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_recent_orders_in_context(self):
        self.client.login(username="testuser", password="TestPass123!")
        Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+380991234567",
            address="123 St",
            city="Kyiv",
            postal_code="01001",
        )
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["orders"]), 1)
