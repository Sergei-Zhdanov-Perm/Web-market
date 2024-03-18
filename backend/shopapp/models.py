from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from myauth.models import ProfileUser
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey


def category_image_directory_path(instance: "Category", filename: str) -> str:
    return f"categories/category_{instance.pk}/image/{filename}"


class Category(MPTTModel):
    title = models.CharField(max_length=200, verbose_name="Название категории")
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=category_image_directory_path,
        default="categories/default.jpg",
        verbose_name="Изображение",
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def get_image(self) -> dict[str: any]:
        image = {
            "src": self.image.url,
            "alt": self.image.name,
        }
        return image

    @staticmethod
    def get_categories() -> list["Category"]:
        """возвращает все категории"""
        categories = Category.objects.filter(parent__isnull=True)
        return categories

    def get_subcategories(self) -> list["Category"]:
        """Возвращает все подкатегории категории"""
        subcategories = self.get_descendants()
        return subcategories

    def __str__(self) -> str:
        return f"{self.title}"


class Tag(models.Model):

    name = models.CharField(max_length=200, verbose_name="Название тега")

    def __str__(self) -> str:
        return f"{self.name}"
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Product(models.Model):

    category = TreeForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
    )
    price = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, verbose_name="Цена"
    )
    count = models.IntegerField(default=0, verbose_name="Количество")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    title = models.CharField(max_length=200, verbose_name="Название продукта")
    description = models.TextField(null=False, blank=True, verbose_name="Описание")
    free_delivery = models.BooleanField(
        default=True, verbose_name="Бесплатная доставка"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Тег", related_name="tags")

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Рейтинг",
    )

    class Meta:
        ordering = ["title", "price"]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def get_image(self) -> list[dict[str: any]]:
        images = ProductImage.objects.filter(product_id=self.pk)
        return [{"src": image.image.url, "alt": image.image.name} for image in images]

    def get_rating(self) -> int:
        reviews = Review.objects.filter(product_id=self.pk).values_list(
            "rate", flat=True
        )
        if reviews.count() == 0:
            rating = 0
            return rating
        rating = sum(reviews) / reviews.count()
        return rating

    def __str__(self) -> str:
        return f"{self.title}"


def product_images_directory_path(instance: Product, filename: str) -> str:
    return f"products/product_{instance.pk}/image/{filename}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to=product_images_directory_path, default="products/default.jpg"
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


class Review(models.Model):
    RATING_CHOICES = [
        (5, "Очень хорошо"),
        (4, "Хорошо"),
        (3, "Нормально"),
        (2, "Плохо"),
        (1, "Очень плохо"),
    ]
    author = models.ForeignKey(
        ProfileUser, on_delete=models.CASCADE, verbose_name="Автор"
    )
    text = models.TextField(blank=True, null=True, verbose_name="Текст отзыва")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания отзыва")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Товар", related_name="reviews"
    )
    rate = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, validators=[MaxValueValidator(5)], verbose_name="Оценка"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self) -> str:
        return str(self.rate)


class Specification(models.Model):
    
    name = models.CharField(max_length=50, blank=True, null=True)
    value = models.CharField(max_length=100, blank=True, null=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

    def __str__(self):
        return f"{self.name}: {self.value}"


class Sale(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="sale_info",
        verbose_name="Продукт",
    )
    date_from = models.DateField(verbose_name="Дата начала скидки")
    date_to = models.DateField(verbose_name="Дата окончания скидки")
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Скидка"
    )

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"


class Basket(models.Model):

    DoesNotExist = "Корзины пока не существует"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_cost(self) -> Decimal:
        return sum([item.product.price * item.quantity for item in self.items.all()])

    def get_products(self) -> list[Product]:
        return [item.product for item in self.items.all()]


class BasketItem(models.Model):

    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="products"
    )
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):

    DELIVERY_OPTIONS = (
        ("delivery", "Доставка"),
        ("express", "Экспресс доставка"),
    )
    PAYMENT_OPTIONS = (
        ("online", "Онлайн оплата"),
        ("online_any", "Онлайн оплата со случайного счета"),
    )

    customer = models.ForeignKey(
        ProfileUser, on_delete=models.CASCADE, verbose_name="Покупатель"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    products = models.ManyToManyField(
        Product, related_name="orders", verbose_name="Продукты"
    )
    city = models.CharField(max_length=100, verbose_name="Город доставки")
    address = models.TextField(max_length=200, verbose_name="Адрес доставки")
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_OPTIONS,
        default="Доставка",
        verbose_name="Тип доставки",
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_OPTIONS,
        default="Онлайн оплата",
        verbose_name="Способ оплаты",
    )
    totalCost = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name="Итоговая сумма заказа",
    )
    status = models.CharField(
        max_length=255, default="inProgress", verbose_name="Статус заказа"
    )
    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE, related_name="order", default=None
    )
    payment_error = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class DeliveryPrice(models.Model):
    

    delivery_cost = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name="Стоимость доставки",
    )

    delivery_express_cost = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name="Стоимость экспресс доставки",
    )

    delivery_free_minimum_cost = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name="Наименьшая сумма для бесплатной доставки",
    )

    class Meta:
        verbose_name = "Стоимость доставки"


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="pay_order")
    card_number = models.CharField(max_length=16)
    validity_period = models.CharField(max_length=20)
    success = models.BooleanField(default=False)
