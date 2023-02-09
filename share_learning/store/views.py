from urllib import request
from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin

from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter

from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .permissions import IsCommentOwner, IsPostOwner, IsSuperOrHasCustomerPermissions, IsSuperOrHasPostPermissionsOrReadOnly, IsSuperUser

from .models import BillingInfo, Cart, CartItem, Customer, Order, OrderItem, Post, PostComment, PostImage


from .serializers import AddCartItemSerializer, BillingInfoSerializer, CartItemSerializer, CartSerializer, CreateBillingInfoSerializer, CreateOrderSerializer, CustomerSerializer, OrderItemSerializer, OrderSerializer, PostCommentSerializer, PostImageSerializer, PostSerializer, UpdateCartItemSerializer, UpdateOrderSerializer


# Create your views here.


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsSuperOrHasCustomerPermissions]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [IsSuperUser()]
    #     return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PATCH'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related('user').all()
    # queryset = Post.objects.prefetch_related('user').all()

    serializer_class = PostSerializer

    # permission_classes = [IsPostOwner]
    # permission_classes = [IsSuperOrHasPostPermissionsOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    def update(self, request, *args, **kwargs):
        logged_in_user = request.user
        post_user_id = request.data['user_id']

        if (int(post_user_id) != logged_in_user.id):
            return Response({'error': 'You can edit only your posts!!'})

        # return super().update(self, request, *args, **kwargs)
        return super().update(request)


class PostImageViewSet(ModelViewSet):
    serializer_class = PostImageSerializer

    def get_queryset(self):
        return PostImage.objects.filter(post_id=self.kwargs['post_pk'])

    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk']}


class PostCommentViewSet(ModelViewSet):

    serializer_class = PostCommentSerializer

    # def get_serializer_class(self):
    #     if self.request.method == 'PATCH':
    #         return PostCommentPatchSerializer
        
    #     return PostCommentSerializer

    # permission_classes = [IsCommentOwner]

    def get_queryset(self):
        return PostComment.objects.filter(post_id = self.kwargs['post_pk'])

    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk']}
    


# class CartViewSet(ModelViewSet):

#     serializer_class = CartSerializer

#     queryset = Cart.objects.all()


class CartViewSet(GenericViewSet, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    # serializer_class = CartItemSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        
        return CartItemSerializer
    

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk'],}
        
    
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')
    

class BillingInfoViewSet(ModelViewSet):
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateBillingInfoSerializer
        return BillingInfoSerializer

    def get_queryset(self):
        return BillingInfo.objects.filter(order_id = self.kwargs['order_pk'])
    

#----------------------- Create Order without involving Cart Starts here-------------------------------
    

# class OrderViewSet(ModelViewSet):

#     filter_backends = [DjangoFilterBackend, SearchFilter]

#     filterset_fields = ['customer_id']

#     # search_fields = ['customer__id']

#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return CreateOrderSerializer
#         return OrderSerializer

#     queryset = Order.objects.all()

#     def get_serializer_context(self):
        
#         return {'user_id': self.request.user.id}


# class OrderItemViewSet(ModelViewSet):
    
#     http_method_names = ['get', 'post', 'patch', 'delete']

#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return AddOrderItemSerializer
#         elif self.request.method == 'PATCH':
#             return UpdateOrderItemSerializer
        
#         return OrderItemSerializer
    

#     def get_serializer_context(self):
#         return {'order_id': self.kwargs['order_pk'],}
        
    
    
#     def get_queryset(self):
#         return OrderItem.objects.filter(order_id = self.kwargs['order_pk']).select_related('product')
    

#----------------------- Create Order without involving Cart Ends here-------------------------------


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if (user.is_staff):
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id=user.id)

        return Order.objects.filter(customer_id=customer_id)
