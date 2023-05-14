# from time import timezone
from django.utils import timezone
from user_panel.models import UserModel, UserModelManager
from rest_framework import serializers
from .models import Food, MenuModel
import datetime
from datetime import date, timedelta
import jdatetime
from jdatetime import datetime as qq


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            return data
        raise serializers.ValidationError('Invalid username or password')


# class AdminUserSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(max_length=100)
#     password = serializers.CharField(max_length=150, write_only=False)
#     name = serializers.CharField(max_length=150, default=None)
#     rank = serializers.CharField(max_length=40, default='Admin')
#
#     class Meta:
#         model = UserModel
#         fields = ('username', 'password', 'name ', 'rank')
#
#     def create(self, validated_data):
#         user = UserModel.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password'],
#         )
#         user.name = validated_data['name']
#         user.is_staff = True
#         user.is_admin = True
#         user.save()
#         return user
class AdminUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=150, write_only=True)
    name = serializers.CharField(max_length=150, default=None)

    class Meta:
        model = UserModel
        fields = ('username', 'password', 'name')

    def validate_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        user.name = validated_data['name']
        user.is_staff = True
        user.is_admin = True
        user.save()
        return user


class CreateUserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=100)
    rank = serializers.CharField(max_length=100)
    package = serializers.CharField(max_length=100)

    def create(self, validated_data):
        user = UserModel.objects.create(
            name=validated_data['name'],
            username=validated_data['username'],
            rank=validated_data['rank'],
            package=validated_data['package'],
            password=validated_data['password']
        )

        user.save()
        return user


class DeleteUserSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.on_deleted = True
        instance.save()
        return instance


class UsersSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    rank = serializers.CharField(max_length=100)
    package = serializers.CharField(max_length=100)
    on_deleted = serializers.BooleanField()

    class Meta:
        model = UserModel
        fields = ('id', 'name', 'username', 'password', 'rank', 'package', 'on_deleted')


class OrderReportSerializer(serializers.Serializer):
    start_date = serializers.CharField(max_length=10)
    end_date = serializers.CharField(max_length=10)

    def validate(self, data):
        start_date_str = data.get("start_date")
        end_date_str = data.get("end_date")

        start_date_j = jdatetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_j = jdatetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        start_date_g = start_date_j.togregorian()
        end_date_g = end_date_j.togregorian()

        data['start_date'] = start_date_g.strftime('%Y-%m-%d')
        data['end_date'] = end_date_g.strftime('%Y-%m-%d')

        if start_date_g > end_date_g:
            raise serializers.ValidationError("start date must be before end date")

        return data


class FinancialReportSerializer(serializers.Serializer):
    start_date = serializers.CharField(max_length=10)
    end_date = serializers.CharField(max_length=10)

    def validate(self, data):
        start_date_str = data.get("start_date")
        end_date_str = data.get("end_date")

        start_date_j = jdatetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_j = jdatetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        start_date_g = start_date_j.togregorian()
        end_date_g = end_date_j.togregorian()

        data['start_date'] = start_date_g.strftime('%Y-%m-%d')
        data['end_date'] = end_date_g.strftime('%Y-%m-%d')

        if start_date_g > end_date_g:
            raise serializers.ValidationError("start date must be before end date")

        return data

    # def validate(self, data):
    #     start_date = data.get("start_date")
    #     end_date = data.get("end_date")
    #     if start_date >= end_date:
    #         raise serializers.ValidationError("start date must be before end date")
    #     yesterday = date.today() - timedelta(days=1)
    #     if end_date > yesterday:
    #         raise serializers.ValidationError("end date must be before today")
    #     return data


class CreateMenuSerializer(serializers.Serializer):
    food_id = serializers.IntegerField()
    date = serializers.CharField(max_length=50)
    number = serializers.IntegerField()



    def validate(self, data):
        date = data.get('date')
        j_date = jdatetime.datetime.strptime(date, '%Y-%m-%d')
        g_date = j_date.togregorian()
        data['date'] = g_date
        if g_date.date() < timezone.now().date():
            raise serializers.ValidationError("you cant set date in past")
        return data

    def create(self, validated_data):
        food = Food.objects.filter(id=validated_data['food_id'], on_deleted=False).exists()
        menu = MenuModel.objects.filter(date=validated_data['date'], on_deleted=False).exists()
        if food and not menu:
            food_instance = Food.objects.get(id=validated_data['food_id'])
            menu = MenuModel.objects.create(food=food_instance, date=validated_data['date'],
                                            number=validated_data['number'])
            menu.save()
            return menu
        else:
            raise serializers.ValidationError("menu allready exists for this date or food not define")



class CreateFoodSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    price = serializers.IntegerField()
    image = serializers.ImageField()

    def create(self, validated_data):
        food = Food.objects.create(
            name=validated_data['name'],
            price=validated_data['price'],
            image=validated_data['image']
        )
        food.save()
        return food


class FoodsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    price = serializers.IntegerField()
    image = serializers.ImageField()
    created_at = serializers.DateField()
    modify_at = serializers.DateField()

    class Meta:
        model = Food
        fields = ('id', 'name', 'price', 'image', 'created_at', 'modify_at')


class DeleteFoodSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.on_deleted = True
        instance.save()
        return instance


class DeleteMenuSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.on_deleted = True
        instance.save()
        return instance


class UpdateFoodSerializer(serializers.Serializer):
    price = serializers.IntegerField()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
