from decimal import Decimal
from rest_framework import serializers

from .models import (
    Product,
    Tag,
    Review,
    ProductImage,
    Specification,
    BasketItem,
    Order,
    Category,
    Sale,
)

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["name"]

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    def get_image(self, obj: Category) -> dict[str: any]:
        return {"src": obj.image.url, "alt": str(obj.image)}

    def get_subcategories(self, obj: Category) -> list[dict[str: any]]:
        children = obj.get_subcategories()
        subcategories = []
        for child in children:
            subcategories.append(
                {
                    "id": child.id,
                    "title": child.title,
                    "image": {"src": child.image.url, "alt": str(child.image)},
                }
            )
        return subcategories

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class ImageSerializer(serializers.ModelSerializer):
    src = serializers.CharField(source="image.url")
    alt = serializers.CharField(source="image.name")

    class Meta:
        model = ProductImage
        fields = ("src", "alt")


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("text", "rate", "date", "author", "email")

    def get_author(self, obj: Review) -> str:
        return f"{obj.author.name} {obj.author.surname}"

    def get_email(self, obj: Review) -> str:
        return {obj.author.email}


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ("name", "value")


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    images = ImageSerializer(many=True)
    reviews = ReviewSerializer(many=True)
    category = serializers.IntegerField(source="category_id")
    rating = serializers.FloatField(source="get_rating")
    specifications = ProductSpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "price",
            "images",
            "tags",
            "reviews",
            "rating",
            "id",
            "category",
            "count",
            "date",
            "description",
            "free_delivery",
            "specifications",
        )

    @staticmethod
    def get_reviews(obj: Product) -> int:
        return obj.reviews.count()


class SaleSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    salePrice = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = ["product", "salePrice", "date_from", "date_to"]

    def get_salePrice(self, obj: Sale) -> Decimal:
        return obj.product.price - obj.discount

    def to_representation(self, instance: Sale) -> dict:
        ret = super().to_representation(instance)
        product_data = ret["product"]
        images = product_data.pop("images", [])
        del ret["product"]
        ret["images"] = images
        ret["id"] = product_data["id"]
        ret["price"] = product_data["price"]
        ret["title"] = product_data["title"]
        ret["dateFrom"] = ret["date_from"]
        ret["dateTo"] = ret["date_to"]
        return ret





class BasketItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = BasketItem
        fields = (
            "product",
            "count",
        )

    def to_representation(self, instance: BasketItem) -> dict:
        data = ProductSerializer(instance.product).data
        data["count"] = instance.quantity
        return data


class OrderSerializer(serializers.ModelSerializer):

    products = ProductSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "customer",
            "delivery_type",
            "payment_type",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        ]

        def to_representation(self, instance: Order) -> dict:
            ret = super().to_representation(instance)
            customer_data = ret["customer"]
            ret["fullName"] = customer_data["name"] + customer_data["surname"]
            ret["email"] = customer_data["email"]
            ret["phone"] = customer_data["phone"]
            ret["deliveryType"] = ret["delivery_type"]
            ret["createdAt"] = ret["created_at"]
            ret["paymentType"] = ret["payment_type"]

            return ret
