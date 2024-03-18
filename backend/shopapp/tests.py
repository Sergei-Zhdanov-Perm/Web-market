from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, Tag, ProductImage, Specification, Order, DeliveryPrice
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer
from myauth.models import ProfileUser
from myauth.serializers import ProfileSerializer

class ShopAppTests(APITestCase):
    def setUp(self) -> None:
        
        self.one_category = Category.objects.create(
            title='Комплектующие для ПК'
        )
        self.one_subcategory = Category.objects.create(
            title='Видеокарты',
            parent=self.one_category
        )
        self.one_tag = Tag.objects.create(
            name='AMD'
        )
        self.popular_tag = Tag.objects.create(
            name='popular'
        )
        self.one_product = Product.objects.create(
            category=self.one_subcategory,
            price=1000.00,
            count=10,
            title='AMD RX 7700XT',
            description='Благодаря архитектуре AMD RDNA 3 она обеспечивает высокий вычислительный потенциал и плавность воспроизведения графики',
            rating=4.95
        )
        self.one_product.tags.add(self.one_tag)
        self.one_product.tags.add(self.popular_tag)
        self.one_product_image = ProductImage.objects.create(
            product=self.one_product
        )
        self.one_specification = Specification.objects.create(
            name='Видеопамять',
            value='12GB',
            product=self.one_product
        )

        self.delivery_price_one = DeliveryPrice.objects.create(delivery_cost=100, delivery_express_cost=500, delivery_free_minimum_cost=1000)

        register_url = reverse('sign-up')
        response = self.client.post(
            register_url, 
            {"username": 'Test', 'name': 'Test', 'password': 'Test'}, 
            format="json"
        )

        
    def test_get_profile(self):
        user = User.objects.get(username='Test')
        profile = ProfileUser.objects.get(user=user)
        serializer = ProfileSerializer(profile)

        profile_url = reverse('profile')
        self.client.force_authenticate(user=user) 
        response = self.client.get(
            profile_url
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_categories(self):
        categories_url = reverse('categories')
        categories = Category.get_categories()
        categories_serialized = CategorySerializer(categories, many=True)
        response = self.client.get(
            categories_url
        )
        self.assertEqual(response.data, categories_serialized.data)

    def test_get_product_detail(self):
        product_detail_url = reverse('product-detail', kwargs={'product_id': 1})
        product = Product.objects.get(pk=1)
        product_serialized = ProductSerializer(product)
        response = self.client.get(
            product_detail_url
        )
        self.assertEqual(response.data, product_serialized.data)

    def test_get_banners(self):
        banner_url = reverse('banners')
        response = self.client.get(
            banner_url,
            {},
            format="json"
        )
        self.assertEqual(1, len(response.data))

    def test_add_review(self):
        user = User.objects.get(username='Test')
        review_url = reverse('product-review', kwargs={'product_id': 1})
        self.client.force_authenticate(user=user) 
        response = self.client.post(
            review_url,
            {'text': 'Good', 'rate': 5}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product_detail_url = reverse('product-detail', kwargs={'product_id': 1})
        response = self.client.get(
            product_detail_url
        )
        self.assertIn('Good', response.data['reviews'][0]['text'])


    def test_get_popular_products(self):
        popular_products_url = reverse('products-popular')
        response = self.client.get(
            popular_products_url
        )
        self.assertEqual(1, len(response.data))

    def test_basket(self):
        user = User.objects.get(username='Test')
        self.client.force_authenticate(user=user) 
        basket_url = reverse('basket')
        response = self.client.post(
            basket_url,
            {'id': 1, 'count': 5}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(1, len(response.data))
        self.assertEqual(5, response.data[0]['count'])        

    def test_post_order(self):
        user = User.objects.get(username='Test')
        self.client.force_authenticate(user=user)
        basket_url = reverse('basket')
        response = self.client.post(
            basket_url,
            {'id': 1, 'count': 5}
        )

        order_url = reverse('orders')
        order_detail_url = reverse('order-detail', kwargs={'order_id': 1})

        response = self.client.post(
            order_url
        )
        self.assertEqual(response.json(), {'orderId': 1})
        order = Order.objects.get(pk=1)
        orders_serialized = OrderSerializer(order)
        response = self.client.get(
            order_detail_url
        )
        self.assertEqual(response.data, orders_serialized.data)

        response = self.client.post(
            order_detail_url,
            {'deliveryType': "Доставка", 'paymentType': 'Онлайн оплата', 'city': 'Moscow', 'address': 'lorem'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_payment(self):
        user = User.objects.get(username='Test')
        self.client.force_authenticate(user=user)
        basket_url = reverse('basket')
        response = self.client.post(
            basket_url,
            {'id': 1, 'count': 5}
        )

        order_url = reverse('orders')
        order_detail_url = reverse('order-detail', kwargs={'order_id': 1})

        response = self.client.post(
            order_url
        )

        order = Order.objects.get(pk=1)
        response = self.client.get(
            order_detail_url
        )

        response = self.client.post(
            order_detail_url,
            {'deliveryType': "Доставка", 'paymentType': 'Онлайн оплата', 'city': 'Moscow', 'address': 'lorem'}
        )

        payment_url = reverse('payment', kwargs={'order_id': 1})
        response = self.client.get(
            payment_url
        )
        self.assertEqual(response.json(), {'status': 'accepted'})

        response = self.client.post(
            payment_url,
            {'number': 12345678, 'month': 12, 'year': 2025, 'code': 123, 'name': 'Test'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            payment_url
        )
        self.assertEqual(response.json(), {'status': 'paid'})

        product_detail_url = reverse('product-detail', kwargs={'product_id': 1})
        response = self.client.get(
            product_detail_url
        )
        self.assertEqual(5, response.data['count'])



    
