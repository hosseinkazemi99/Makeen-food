from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .permissions import IsAdminOrReadOnly
from .serializers import LoginSerializer, CreateUserSerializer, OrderReportSerializer, FinancialReportSerializer, \
    UsersSerializers, CreateFoodSerializer, FoodsSerializer, UpdateFoodSerializer, DeleteFoodSerializer, \
    DeleteUserSerializer, CreateMenuSerializer, DeleteMenuSerializer, AdminUserSerializer
from user_panel.models import UserModel

from .models import MenuModel, Food
import jdatetime


class LoginPanel(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request=request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            response_data = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }
            return Response(data=response_data, status=status.HTTP_200_OK)

        return Response({'Invalid': 'Username and password are wrong'}, status=status.HTTP_403_FORBIDDEN)
class AdminUser(APIView):
    def post(self, request):
        serializer = AdminUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)



class CreateUser(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status.HTTP_200_OK, status=status.HTTP_200_OK)


class DeleteUser(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, id):
        try:
            user = UserModel.objects.get(id=id, on_deleted=False)
        except UserModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DeleteUserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status.HTTP_200_OK, status.HTTP_200_OK)


class Users(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        users = UserModel.objects.filter(on_deleted=False)
        serializer = UsersSerializers(users, many=True)
        return Response(serializer.data, status.HTTP_200_OK)



class CreateMenu(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        serializer = CreateMenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)





class OrderReport(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        serializer = OrderReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        menus = MenuModel.objects.filter(date__range=(start_date, end_date),on_deleted=False)
        data = []
        for menu in menus:
            j_date = jdatetime.datetime.fromgregorian(date=menu.date).strftime('%Y-%m-%d')
            data.append({
                'id':menu.id,
                'date': j_date,
                'day_of_week': menu.day_of_week,
                'food': menu.food.name,
                'number':menu.number,
                'quantity': menu.quantity,

            })
        return Response(data, status=status.HTTP_200_OK)


class FinancialReport(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        serializer = FinancialReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        menus = MenuModel.objects.filter(date__range=(start_date, end_date), on_deleted=False)
        data = []
        for menu in menus:
            j_date = jdatetime.datetime.fromgregorian(date=menu.date).strftime('%Y-%m-%d')
            data.append({
                'date': j_date,
                'quantity': menu.quantity,
                'sell': (menu.price) * (menu.quantity),
                'food': menu.food.name
            })

        return Response(data, status=status.HTTP_200_OK)


class CreateFood(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        serializer = CreateFoodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status.HTTP_200_OK, status=status.HTTP_200_OK)


class Foods(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        try:
            foods = Food.objects.filter(on_deleted=False)
        except:
            return Response(status.HTTP_400_BAD_REQUEST, status.HTTP_400_BAD_REQUEST)
        serializer = FoodsSerializer(foods, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class DeleteFood(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, id):
        try:
            food = Food.objects.get(id=id, on_deleted=False)
        except Food.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DeleteFoodSerializer(food, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

class DeleteMenu(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, id):
        try:
            menu = MenuModel.objects.get(id=id, on_deleted=False)
        except MenuModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DeleteMenuSerializer(menu, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)



class UpdateFood(APIView):

    def put(self, request, id):
        try:
            food = Food.objects.get(id=id)
        except Food.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateFoodSerializer(food, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
