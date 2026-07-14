from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate

from user_panel.models import UserModel
from .permissions import IsAdminOrReadOnly, IsAdmin
from .pagination import OrderReportPagination, AllUsersPagination, AllFoodsPagination
from . import serializers 
from .models import MenuModel, Food



class LoginPanelApiView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = []

    serializer_class = serializers.LoginPanelApiViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"Invalid": "Username and password are wrong"},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

class CreateAdminApiView(generics.CreateAPIView):
    serializer_class = serializers.CreateAdminApiViewSerializer
    permission_classes = [IsAdmin]

class CreateUserApiView(generics.CreateAPIView):
    serializer_class = serializers.CreateUserApiViewSerializer
    permission_classes = [IsAdmin]

class DeleteUserApiView(generics.DestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = UserModel.objects.filter(on_deleted=False)

    def perform_destroy(self, instance):
        instance.on_deleted = True
        instance.save(update_fields=["on_deleted"])

class AllUsersApiView(generics.ListAPIView):
    serializer_class = serializers.AllUsersApiViewSerializer
    permission_classes = [IsAdmin]
    queryset = UserModel.objects.filter(on_deleted=False)
    pagination_class = AllUsersPagination

class OrderReportApiView(APIView):
    permission_classes = [IsAdmin]
    pagination_class = OrderReportPagination
    @extend_schema(
            request=serializers.OrderReportApiViewSerializer,
            responses=serializers.OrderReportResultApiViewSerializer(many=True)
    )
    def post(self, request):
        serializer = serializers.OrderReportApiViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menus = MenuModel.objects.filter(
            date__range=(
                serializer.validated_data["start_date"],
                serializer.validated_data["end_date"],
            ),
            on_deleted=False,
        )

        result = serializers.OrderReportResultApiViewSerializer(
            menus,
            many=True,
        )

        return Response(
            result.data,
            status=status.HTTP_200_OK,
        )

class FinancialReportApiView(APIView):
    permission_classes = [IsAdmin]
    @extend_schema(
            request=serializers.FinancialReportApiViewSerializer,
            responses=serializers.FinancialReportResponseApiViewSerializer(many=False)
    )
    def post(self, request):
        serializer = serializers.FinancialReportApiViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menus = MenuModel.objects.filter(
            date__range=(serializer.validated_data["start_date"],serializer.validated_data["end_date"]),
            on_deleted=False
            )
        total_sell = 0
        total_quantity = 0

        for menu in menus:
            total_sell += menu.price * menu.quantity
            total_quantity += menu.quantity
        response = serializers.FinancialReportResponseApiViewSerializer({
            "total_sell": total_sell,
            "total_quantity": total_quantity
            })
        return Response(response.data, status=status.HTTP_200_OK)

class AllFoodsApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AllFoodsApiViewSerializer
    queryset = Food.objects.filter(on_deleted=False)
    pagination_class = AllFoodsPagination

class CreateMenuApiView(generics.CreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = serializers.CreateMenuApiViewSerializer

class CreateFoodApiView(generics.CreateAPIView):
    serializer_class = serializers.CreateFoodApiViewSerializer
    permission_classes = [IsAdmin]
    queryset = Food.objects.all()
    parser_classes = [MultiPartParser, FormParser]

class DeleteFoodApiView(generics.DestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = Food.objects.filter(on_deleted=False)

    def perform_destroy(self, instance):
        instance.on_deleted = True
        instance.save(update_fields=["on_deleted"])

class DeleteMenuApiView(generics.DestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = MenuModel.objects.filter(on_deleted=False)

    def perform_destroy(self, instance):
        instance.on_deleted = True
        instance.save(update_fields=["on_deleted"])

class UpdateFoodApiView(generics.UpdateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = serializers.UpdateFoodApiViewSerializer
    queryset = Food.objects.filter(on_deleted=False)
