from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from myauth.views import (
    SignOutAPIView,
    SignInAPIView,
    SignUpAPIView,
    ProfileUserAPIView,
    AvatarChangeAPIView,
    ChangePasswordAPIView,
)

from shopapp.views import (
    CategoryView,
    CatalogView,
    BannerListView,
    PopularListView,
    LimitedListView,
    ProductDetailView,
    ProductReviewView,
    TagsListView,
    SalesListView,
    BasketView,
    OrderView,
    OrderDetailView,
    PaymentView,
)

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(
        "schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("sign-out", SignOutAPIView.as_view()),
    path("sign-in", SignInAPIView.as_view()),
    path("sign-up", SignUpAPIView.as_view(), name='sign-up'),
    path("profile", ProfileUserAPIView.as_view(), name='profile'),
    path("profile/avatar", AvatarChangeAPIView.as_view()),
    path("profile/password", ChangePasswordAPIView.as_view()),
    path("categories", CategoryView.as_view(), name='categories'),
    path("catalog", CatalogView.as_view()),
    path("banners", BannerListView.as_view(), name='banners'),
    path("tags", TagsListView.as_view()),
    path("products/popular", PopularListView.as_view(), name='products-popular'),
    path("products/limited", LimitedListView.as_view()),
    path("sales", SalesListView.as_view()),
    path("product/<int:product_id>", ProductDetailView.as_view(), name='product-detail'),
    path("product/<int:product_id>/reviews", ProductReviewView.as_view(), name='product-review'),
    path("basket", BasketView.as_view(), name='basket'),
    path("orders", OrderView.as_view(), name='orders'),
    path("order/<int:order_id>", OrderDetailView.as_view(), name='order-detail'),
    path("payment/<int:order_id>", PaymentView.as_view(), name='payment'),
]
