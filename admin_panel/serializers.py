from django.utils import timezone
from user_panel.models import UserModel
from rest_framework import serializers
from .models import Food, MenuModel
import jdatetime


class LoginPanelApiViewSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

class CreateAdminApiViewSerializer(serializers.Serializer):
    username = serializers.CharField()

    def save(self):
        try:
            user = UserModel.objects.get(username=self.validated_data["username"])
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        user.is_staff = True
        user.is_admin = True
        user.save()

        return user

class CreateUserApiViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("name", "username", "password", "rank", "package",)
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)

class AllUsersApiViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "name", "username", "rank", "package",)
        extra_kwargs = {
            "password": {"write_only": True}
        }

class OrderReportApiViewSerializer(serializers.Serializer):
    start_date = serializers.CharField(max_length=10)
    end_date = serializers.CharField(max_length=10)

    def validate(self, attrs):
        try:
            start_date = jdatetime.datetime.strptime(attrs["start_date"], "%Y-%m-%d").togregorian().date()
            end_date = jdatetime.datetime.strptime(attrs["end_date"], "%Y-%m-%d").togregorian().date()

        except ValueError:
            raise serializers.ValidationError("Invalid date format.")

        if start_date > end_date:
            raise serializers.ValidationError("start_date must be before end_date.")

        attrs["start_date"] = start_date
        attrs["end_date"] = end_date

        return attrs

class OrderReportResultApiViewSerializer(serializers.ModelSerializer):
    food = serializers.CharField(source="food.name")
    date = serializers.SerializerMethodField()

    class Meta:
        model = MenuModel
        fields = (
            "id",
            "date",
            "day_of_week",
            "food",
            "number",
            "quantity",
        )

    def get_date(self, obj):
        return jdatetime.datetime.fromgregorian(
            date=obj.date
        ).strftime("%Y-%m-%d")

class FinancialReportApiViewSerializer(serializers.Serializer):
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

class FinancialReportResponseApiViewSerializer(serializers.Serializer):
    total_sell = serializers.IntegerField()
    total_quantity = serializers.IntegerField()

class CreateMenuApiViewSerializer(serializers.Serializer):
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
            raise serializers.ValidationError("menu already exists for this date or food not define")

class CreateFoodApiViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ("name", "price", "image")

class AllFoodsApiViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ("id", "name", "price", "image")

class UpdateFoodApiViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ("name", "price", "image")
