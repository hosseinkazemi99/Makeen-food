from rest_framework import serializers
from admin_panel.models import MenuModel
import jdatetime
from datetime import timedelta
from jdatetime import date as jdate
from jdatetime import datetime as jalalidatetime

from .models import CartItem, Cart, UserModel, Wallet, Transaction, Payment

class LoginUserApiViewSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=100)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = UserModel.objects.filter(username=username, password=password)
        if not user:
            raise serializers.ValidationError('username or password wrong')

        return attrs

class ShowMenuApiViewSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    food_name = serializers.CharField(source='food.name')
    image = serializers.ImageField(source="food.image", read_only=True)

    class Meta:
        model = MenuModel
        fields = ('id', 'food_name', 'date', 'day_of_week', 'number', 'image', 'price')

    def get_date(self, obj):
        return jdate.fromgregorian(date=obj.date).strftime("%Y-%m-%d")

class ShowOrderApiViewSerializer(serializers.ModelSerializer):
    menu_food_name = serializers.CharField(source='menu.food.name',read_only=True)
    date = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('menu_food_name', 'date', 'quantity', 'total_price')

    def get_date(self, obj):
        return jalalidatetime.fromgregorian(date=obj.menu.date).strftime('%Y-%m-%d')

class CartItemApiViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('id', 'menu', 'price', 'quantity', 'total_price')

class GetCartApiViewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('user', 'is_paid', 'total_price')

class UpdateCartItemApiViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("quantity",)

    def validate_quantity(self, value):
        menu = self.instance.menu

        if value > menu.number:
            raise serializers.ValidationError(
                "غذا به این تعداد موجود نیست."
            )

        return value

class CreateCartItemApiViewSerializer(serializers.ModelSerializer):
    menu_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ("menu_id", "quantity")

    def validate(self, attrs):
        try:
            menu = MenuModel.objects.get(id=attrs["menu_id"], on_deleted=False,)
        except MenuModel.DoesNotExist:
            raise serializers.ValidationError("Menu not found.")

        if menu.number < attrs["quantity"]:
            raise serializers.ValidationError("غذا به این تعداد موجود نیست.")

        attrs["menu"] = menu
        return attrs

    def create(self, validated_data):
        menu = validated_data.pop("menu")
        validated_data.pop("menu_id")
        cart, _ = Cart.objects.get_or_create(user=self.context["request"].user, is_paid=False,)
        return CartItem.objects.create(cart=cart, menu=menu, price=menu.price, **validated_data,)

class ShowAllCartItemApiViewSerializer(serializers.ModelSerializer):
    menu = serializers.CharField(source='menu.food.name', read_only=True)

    class Meta:
        model = CartItem
        fields = ('id','menu', 'quantity', 'price', 'total_price')

class TransactionApiViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ("type", "amount", "timestamp")

    def get_timestamp(self, obj):
        timestamp = obj.timestamp + timedelta(hours=3, minutes=30)
        return jdatetime.datetime.fromgregorian(
            datetime=timestamp
        ).strftime("%Y-%m-%d %H:%M:%S")

class WalletApiViewSerializer(serializers.ModelSerializer):
    transactions = TransactionApiViewSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Wallet
        fields = ("balance", "transactions")

class PaymentApiViewSerializer(serializers.Serializer):
    order_number = serializers.IntegerField(min_value=1000000,max_value=9999999)
