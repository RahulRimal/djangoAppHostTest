from cgitb import lookup
from django.contrib import admin
from django.urls import path, include

from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()

router.register('customers', views.CustomerViewSet)
router.register('posts', views.PostViewSet, basename='posts')
router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')

posts_router = routers.NestedDefaultRouter(router, 'posts', lookup='post')
posts_router.register('images', views.PostImageViewSet, basename='post-images')
posts_router.register('comments', views.PostCommentViewSet, basename='post-comments')

customers_router = routers.NestedDefaultRouter(router, 'customers', lookup='customer')
customers_router.register('comments', views.PostCommentViewSet, basename='customer-comments')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

orders_router = routers.NestedDefaultRouter(router, 'orders', lookup='order')
# orders_router.register('items', views.OrderItemViewSet, basename='order-items')
orders_router.register('billing_info', views.BillingInfoViewSet, basename='billing-info')

urlpatterns = router.urls + posts_router.urls + customers_router.urls + carts_router.urls + orders_router.urls


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('store.urls')),
# ]
