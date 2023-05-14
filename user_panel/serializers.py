from rest_framework import serializers
from admin_panel.models import MenuModel
import jdatetime
from datetime import timedelta

from jdatetime import date as jdate
from jdatetime import datetime as jdatetime
from datetime import datetime
from .models import CartItem, Cart, UserModel, Wallet, Transaction, Payment


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=100)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = UserModel.objects.filter(username=username, password=password)
        if not user:
            raise serializers.ValidationError('username or password wrong')

        return attrs


class ShowMenuSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    food_name = serializers.CharField(source='food.name')

    def get_date(self, obj):
        return jdate.fromgregorian(date=datetime.strptime(str(obj.date), '%Y-%m-%d')).strftime('%Y-%m-%d')

    class Meta:
        model = MenuModel
        fields = ('id', 'food_name', 'food', 'date', 'day_of_week', 'number', 'image', 'price')
class ShowOrderSerializer(serializers.ModelSerializer):
    menu_food_name = serializers.CharField(source='menu.food.name')
    date = serializers.SerializerMethodField()
    quantity = serializers.IntegerField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('menu_food_name', 'date', 'quantity', 'total_price')

    def get_total_price(self, obj):
        return obj.total_price

    def get_date(self, obj):
        return jdatetime.fromgregorian(date=obj.menu.date).strftime('%Y-%m-%d')

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('id', 'menu', 'price', 'quantity', 'total_price')


class GetCartSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('user', 'is_paid', 'total_price')

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, max_value=40)


class CreateCartItemSerializer(serializers.Serializer):
    menu_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    def validate(self, attrs):
        quantity = attrs.get("quantity")
        menu_id = attrs.get("menu_id")
        menu = MenuModel.objects.filter(id=menu_id).exists()
        if not menu:
            raise serializers.ValidationError('menu id is not define')
        menu = MenuModel.objects.get(id=menu_id)
        if menu.number - quantity < 0 :
            raise serializers.ValidationError("غذا به این تعداد موجود نیست")
        return attrs


class ShowAllCartItemSerializer(serializers.ModelSerializer):
    menu = serializers.CharField(source='menu.food.name')

    class Meta:
        model = CartItem
        fields = ('id','menu', 'quantity', 'price', 'total_price')

class WalletSerializer(serializers.Serializer):
    wallet = serializers.SerializerMethodField()
    transactions = serializers.SerializerMethodField()

    def get_wallet(self, obj):
        return {
            'balance': obj['wallet'].balance,
        }

    def get_transactions(self, obj):
        transaction_data = []
        for transaction in obj['transactions']:
            timestamp = transaction.timestamp + timedelta(hours=3, minutes=30)
            j_timestamp = jdatetime.datetime.fromgregorian(datetime=timestamp).strftime('%Y-%m-%d %H:%M:%S')
            transaction_data.append({
                'type': transaction.type,
                'amount': transaction.amount,
                'timestamp': j_timestamp,
            })
        return transaction_data




class PaymentSerializer(serializers.Serializer):
    order_number = serializers.IntegerField(min_value=1000000,max_value=9999999)
