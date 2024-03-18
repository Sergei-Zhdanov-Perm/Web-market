import datetime

from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .models import (
    Category,
    Product,
    Review,
    Tag,
    Sale,
    Basket,
    BasketItem,
    DeliveryPrice,
    Order,
    Payment,
)
from .serializers import (
    TagSerializer,
    ProductSerializer,
    BasketItemSerializer,
    OrderSerializer,
    CategorySerializer,
    SaleSerializer,
)
from myauth.models import ProfileUser


class CategoryView(APIView):

    def get(self, request: HttpRequest) -> Response:
        categories = Category.get_categories()
        categories_serialized = CategorySerializer(categories, many=True)
        return Response(categories_serialized.data)


class CatalogView(APIView):
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = {
        "category": ["exact"], 
        "price": ["gte", "lte"], 
        "freeDelivery": ["exact"], 
        "count": ["gt"], 
        "title": ["icontains"], 
        "tags__name": ["exact"], 
    }

    ordering_fields = [
        "id",
        "category__id",
        "price",
        "count",
        "date",
        "title",
        "freeDelivery",
        "rating",
    ]

    def filter_queryset(self, products: QuerySet[Product]) -> QuerySet[Product]:
        category_id: int = self.request.GET.get("category")
        min_price: float = float(self.request.GET.get("filter[minPrice]", 0))
        max_price: float = float(self.request.GET.get("filter[maxPrice]", float("inf")))
        free_delivery: bool = (
            self.request.GET.get("filter[freeDelivery]", "").lower() == "true"
        )
        available: bool = self.request.GET.get("filter[available]", "").lower() == "true"
        name: str = self.request.GET.get("filter[name]", "").strip()
        tags: list[str] = self.request.GET.getlist("tags[]")
        sort_field: str = self.request.GET.get("sort", "id")
        sort_type: str = self.request.GET.get("sortType", "inc")

        if category_id:
            products = products.filter(category__id=category_id)
        products = products.filter(price__gte=min_price, price__lte=max_price)
        if free_delivery:
            products = products.filter(free_delivery=True)
        if available:
            products = products.filter(count__gt=0)
        if name:
            products = products.filter(title__icontains=name)
        for tag in tags:
            products = products.filter(tags__name=tag)
        if sort_type == "inc":
            products = products.order_by(sort_field)
        else:
            products = products.order_by("-" + sort_field)

        return products

    def get(self, request: HttpRequest) -> Response:
        products = Product.objects.all()
        filtered_products = self.filter_queryset(products)
        page_number: int = int(request.GET.get("currentPage", 1))
        limit: int = int(request.GET.get("limit", 20))
        paginator = Paginator(filtered_products, limit)
        page = paginator.get_page(page_number)
        products_serialized = ProductSerializer(page, many=True)
        catalog_data: dict[str: any] = {
            "items": products_serialized.data,
            "currentPage": page_number,
            "lastPage": paginator.num_pages,
        }
        return Response(catalog_data)


class BannerListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(rating__gt=0).order_by("-rating")[:3]

    def list(self, request: HttpRequest, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PopularListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # после реализации заказов подставить - .order_by("-countOfOrders")[:8]
        return Product.objects.filter(tags__name__in=["popular"])[:8]

    def list(self, request: HttpRequest, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LimitedListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(tags__name__in=["limited"])[:16]

    def list(self, request: HttpRequest, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    def get(self, request: HttpRequest, product_id) -> Response:
        product = Product.objects.get(id=product_id)
        product_serializer = ProductSerializer(product)
        return Response(product_serializer.data)


class ProductReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, product_id) -> Response:
        profile = ProfileUser.objects.get(user=request.user)
        product = Product.objects.get(pk=product_id)
        text = request.data["text"]
        rate = request.data["rate"]

        review = Review.objects.create(
            author=profile,
            text=text,
            rate=rate,
            product=product,
        )
        review.save()
        return Response(status=201)


class TagsListView(ListAPIView):
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.all().distinct()

    def list(self, request: HttpRequest, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SalesListView(APIView):
    def get(self, request: HttpRequest) -> Response:
        page_number: int = int(request.GET.get("currentPage", 1))
        limit: int = int(request.GET.get("limit", 20))
        obj_list: list[Sale] = [obj for obj in Sale.objects.all()]
        paginator = Paginator(obj_list, limit)
        page = paginator.get_page(page_number)
        serialized_data = SaleSerializer(page, many=True)
        response_data: dict[str: any] = {
            "items": serialized_data.data,
            "currentPage": page_number,
            "lastPage": paginator.num_pages,
        }
        return Response(response_data)


class BasketView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest) -> Response:
        queryset = BasketItem.objects.filter(basket__user=request.user)
        serializer = BasketItemSerializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request: HttpRequest) -> Response:
        id: int = request.data["id"]
        count: int = int(request.data["count"])
        product = Product.objects.get(id=id)

        if product.count - count < 0:
            return Response(status=400)

        basket, created = Basket.objects.get_or_create(user=request.user)

        if created:
            basket_item = BasketItem.objects.create(
                basket=basket, product=product, quantity=count
            )
        else:
            basket_item, created = BasketItem.objects.get_or_create(
                basket=basket, product=product
            )
            if created:
                basket_item.product = product
                basket_item.quantity = count
                basket_item.save()
            else:
                basket_item.quantity += count
                if basket_item.quantity > product.count:
                    return Response(status=400)
                basket_item.save()

        basket_items = BasketItem.objects.filter(basket=basket)
        serializer = BasketItemSerializer(basket_items, many=True)

        return Response(serializer.data, status=201)

    def delete(self, request: HttpRequest) -> Response:
        id: int = request.data["id"]
        count: int = request.data["count"]

        try:
            basket: Basket = request.user.basket
            product = Product.objects.get(id=id)
            basket_item = BasketItem.objects.get(basket=basket, product=product)
            if basket_item.quantity > count:
                basket_item.quantity -= (
                    count 
                )
                basket_item.save()
            else:
                basket_item.delete()

            basket_items = BasketItem.objects.filter(basket=basket)
            serializer = BasketItemSerializer(basket_items, many=True)

            return Response(serializer.data)
        except Basket.DoesNotExist:
            return Response("Товары в корзине не найдены", status=404)


class OrderView(APIView):

    def get(self, request: HttpRequest) -> Response:
        profile = ProfileUser.objects.get(user=request.user)
        orders = Order.objects.filter(customer=profile)
        orders_serialized = OrderSerializer(orders, many=True)
        return Response(orders_serialized.data)

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            basket: Basket = request.user.basket
            profile = ProfileUser.objects.get(user=request.user)
            total_cost = basket.get_total_cost()
            order = Order.objects.create(
                customer=profile,
                basket=basket,
            )
            delivery_price = DeliveryPrice.objects.get(id=1)
            if total_cost > delivery_price.delivery_free_minimum_cost:
                order.totalCost = total_cost
            else:
                order.totalCost = total_cost + delivery_price.delivery_cost
            products = basket.get_products()
            order.products.set(products)
            request.session["products"] = request.data
            order.save()
            response_data = {"orderId": order.pk}
            return JsonResponse(response_data)
        except Basket.DoesNotExist:
            error_data = {"error": "У данного пользователя пока нет 'корзины'"}
            return JsonResponse(error_data)


class OrderDetailView(APIView):
    def get(self, request: HttpRequest, order_id: int) -> Response:
        order = Order.objects.get(pk=order_id)
        serializer = OrderSerializer(order)
        if "products" in request.session:
            products = request.session["products"]
            for i, product in enumerate(serializer.data["products"]):
                try:
                    product["count"] = products[i]["count"]
                except KeyError:
                    continue
        return Response(serializer.data)

    def post(self, request: HttpRequest, order_id: int) -> Response:
        order = get_object_or_404(Order, id=order_id)

        delivery_type: str = request.data["deliveryType"]
        payment_type: str = request.data["paymentType"]
        city: str = request.data["city"]
        address: str = request.data["address"]
        status_order = "accepted"

        if delivery_type == "express":
            delivery_price = DeliveryPrice.objects.get(id=1)
            order.totalCost += delivery_price.delivery_express_cost
            order.save()

        order.delivery_type = delivery_type
        order.payment_type = payment_type
        order.city = city
        order.address = address
        order.status = status_order
        order.save()

        response_data = {"orderId": order.id}
        return Response(response_data, status=200)


class PaymentView(APIView):
    def get(self, request: HttpRequest, order_id: int) -> JsonResponse:
        order = get_object_or_404(Order, id=order_id)
        return JsonResponse({"status": order.status})

    def post(self, request: HttpRequest, order_id: int) -> JsonResponse | HttpResponse:
        data = request.data
        card_number: str = data["number"]
        expiration_month: str = data["month"]
        expiration_year: str = data["year"]
        cvv_code = data["code"]
        card_holder_name = data["name"]
        current_year = datetime.datetime.now().year % 100

        if int(expiration_year) < current_year or (
            int(expiration_year == current_year)
            and int(expiration_month) < datetime.datetime.now().month
        ):
            order = Order.objects.get(id=order_id)
            order.payment_error = "Payment expired"
            order.save()
            return JsonResponse({"error": "Payment expired"}, status=500)

        if len(card_number.strip()) > 8 and int(card_number) % 2 != 0:
            return JsonResponse(
                {"error": "Неверный номер банковской карты"}, status=400
            )

        res_date = f"{expiration_month}.{expiration_year}"
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.create(
            order=order, card_number=card_number, validity_period=res_date
        )

        basket = Basket.objects.get(user=request.user)
        basket_items = BasketItem.objects.filter(basket=basket)
        for basket_item in basket_items:
            product = Product.objects.get(pk=basket_item.product.pk)
            if product.count < basket_item.quantity:
                return JsonResponse(
                    {"error": "Недостаточно товаров в наличии"}, status=400
                )
            product.count -= basket_item.quantity
            product.save()
            payment.success = True
            payment.save()
        basket_items.delete()

        order.status = "paid"
        order.save()
        return HttpResponse(status=200)
