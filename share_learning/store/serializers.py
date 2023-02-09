
import sys
from rest_framework import serializers
from django.db import transaction


from .models import BillingInfo, CartItem, Customer, Order, OrderItem, Post, PostComment, PostImage, Cart


class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id', read_only=True)
    # class' = serializers.CharField(source='user_class')

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email', 'description', 'image', 'user_class', 'created_at']


class SimpleCustomerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = Customer
        # model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class PostImageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        post_id = self.context['post_id']
        return PostImage.objects.create(post_id=post_id, **validated_data)

    class Meta:
        model = PostImage
        fields = ['id', 'image']


class PostSerializer(serializers.ModelSerializer):
    user = SimpleCustomerSerializer(read_only=True)
    # user = SimpleCustomerSerializer()
    # id = serializers.IntegerField(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'book_name', 'author', 'description', 'bought_date',
                  'unit_price', 'book_count', 'images', 'wishlisted', 'post_type', 'post_rating', 'posted_on']
        

class SimplePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['id', 'book_name', 'unit_price']


class PostCommentSerializer(serializers.ModelSerializer):
    # user_id = serializers.IntegerField(source='user_id', read_only=True)
    user_id = serializers.IntegerField()
    

    def create(self, validated_data):
        post_id = self.context['post_id']
        return PostComment.objects.create(post_id=post_id, **validated_data)
    
    class Meta:
        model = PostComment
        fields = ['id', 'user_id', 'post_id', 'comment_body', 'created_date']

        

# class PostCommentPatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostComment
#         fields = ['id', 'comment_body']



class CartItemSerializer(serializers.ModelSerializer):

    product = SimplePostSerializer()

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, item:CartItem):
        return item.quantity * item.product.unit_price


    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Post.objects.filter(pk=value).exists():
            raise serializers.ValidationError ('No product with the given id was found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance



    class Meta:
        model = CartItem
        fields = ['id','product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])


    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']







class BillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingInfo
        fields = ['first_name', 'last_name',
                  'phone', 'email', 'convenient_location', 'side_note']
        
class CreateBillingInfoSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField()
    class Meta:
        model = BillingInfo
        fields = ['first_name', 'last_name',
                  'phone', 'email', 'convenient_location', 'side_note', 'order_id']
        


#----------------------- Create Order without involving Cart Starts here-------------------------------

# class OrderItemSerializer(serializers.ModelSerializer):
#     product = SimplePostSerializer()

#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'quantity']


# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     billing_info = BillingInfoSerializer(read_only=True)
#     customer = SimpleCustomerSerializer(read_only=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'customer', 'items', 'payment_status', 'billing_info', 'placed_at']


# class CreateOrderSerializer(serializers.ModelSerializer):
#     def save(self, **kwargs):
#         customer_id = self.context['user_id']
#         payment_status = self.validated_data['payment_status']
#         self.instance = Order.objects.create(customer_id = customer_id, **self.validated_data)
#         # self.instance = Order.objects.create(customer_id = customer_id, payment_status = payment_status, **self.validated_data)
        

#         return self.instance

#     class Meta:
#         model = Order
#         fields = ['id', 'payment_status']



# class UpdateOrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ['payment_status', 'billing_info']


# class AddOrderItemSerializer(serializers.ModelSerializer):

#     product_id = serializers.IntegerField()

#     def validate_product_id(self, value):
#         if not Post.objects.filter(pk=value).exists():
#             raise serializers.ValidationError ('No product with the given id was found')
#         return value

#     def save(self, **kwargs):
#         order_id = self.context['order_id']
#         product_id = self.validated_data['product_id']
#         quantity = self.validated_data['quantity']

#         try:
#             order_item = OrderItem.objects.get(order_id=order_id, product_id=product_id)
#             order_item.quantity += quantity
#             order_item.save()
#             self.instance = order_item
#         except OrderItem.DoesNotExist:
#             self.instance = OrderItem.objects.create(order_id=order_id, **self.validated_data)

#         return self.instance



#     class Meta:
#         model = OrderItem
#         fields = ['id','product_id', 'quantity']


# class UpdateOrderItemSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = OrderItem
#         fields = ['quantity']


#----------------------- Create Order without involving Cart Ends here-------------------------------


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimplePostSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    billing_info = BillingInfoSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'payment_status', 'billing_info', 'placed_at']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    billing_info = BillingInfoSerializer()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            (customer, created) = Customer.objects.get_or_create(
                user_id=self.context['user_id'])

        order = Order.objects.create(
            customer=customer)
        billing_info = BillingInfo.objects.create(
            ** self.validated_data['billing_info'], order=order)
        cart_items = CartItem.objects.select_related(
            'product').filter(cart_id=cart_id)
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
            ) for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        Cart.objects.filter(pk=cart_id).delete()

        return order
