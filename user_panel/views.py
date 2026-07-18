import os
import datetime
import requests
from dotenv import load_dotenv

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from admin_panel.models import MenuModel

from . import serializers 
from .models import CartItem, Cart, Wallet, Payment, Transaction


load_dotenv()

class ShowMenuApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ShowMenuApiViewSerializer
    queryset = MenuModel.objects.select_related("food").filter(date__gte=datetime.date.today(),on_deleted=False,)

class ShowOrderApiView(generics.ListAPIView):
    serializer_class = serializers.ShowOrderApiViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CartItem.objects
            .select_related("menu", "menu__food")
            .filter(
                menu__date__gte=datetime.date.today(),
                cart__user=self.request.user,
                on_deleted=False,
            )
        )

class GetCartApiView(generics.RetrieveAPIView):
    serializer_class = serializers.GetCartApiViewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user,
            is_paid=False,
        )
        return cart

class CreateCartItemApiView(generics.CreateAPIView):
    serializer_class = serializers.CreateCartItemApiViewSerializer
    permission_classes = [IsAuthenticated]

class ShowAllCartItemApiView(generics.ListAPIView):
    serializer_class = serializers.ShowAllCartItemApiViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            CartItem.objects
            .select_related("menu", "menu__food", "cart")
            .filter(
                cart__user=self.request.user,
                cart__is_paid=False,
                on_deleted=False,
            )
        )

class UpdateCartItemApiView(generics.UpdateAPIView):
    serializer_class =  serializers.UpdateCartItemApiViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user,
            on_deleted=False,
        )

class CancelCartItemApiView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class WalletDetailApiView(generics.RetrieveAPIView):
    serializer_class = serializers.WalletApiViewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Wallet.objects.prefetch_related(
            "transactions"
        ).get(
            user=self.request.user
        )

###########################

USE_FAKE_PAYMENT = os.getenv("USE_FAKE_PAYMENT", False)
class NextPayCreatePaymentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        last_order = Payment.objects.order_by("-id").first()
        order = last_order.order_number + 1 if last_order else 1000000
        user = request.user
        cart = Cart.objects.filter(user=user, is_paid=False).exists()
        if not cart:
            return Response({'error': "سفارشی وجود ندارد "})
        cart = Cart.objects.get(user=user, is_paid=False)
        cart_items = cart.cartitem.filter(on_deleted=False)
        for cart_item in cart_items:
            menu = cart_item.menu
            if menu.number - cart_item.quantity < 0:
                return Response({"خطا": "سفارش موجود نمیباشد "})
        payment = Payment.objects.create(user=user, amount=cart.total_price, order_number=order)
        if USE_FAKE_PAYMENT:
            payment.status = Payment.PENDING
            payment.transaction_id = "TEST_TRANSACTION_ID"
            payment.save()

            return Response(
                {
                    "order_number": payment.order_number,
                    "trans_id": payment.transaction_id,
                },
                status=status.HTTP_200_OK,
            )
        url = 'https://nextpay.org/nx/gateway/token'

        data = {
            'api_key': os.environ.get('PEYMENT-KEY'),
            'amount': payment.amount,
            'order_id': payment.id,
            'callback_uri': os.environ.get('URLBACK'),
        }

        headers = {
            'User-Agent': 'PostmanRuntime/7.26.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url=url, headers=headers, data=data)
        if response.status_code == status.HTTP_200_OK:
            result = response.json()
            print(result)
            if result['code'] == -1:
                payment.status = Payment.PENDING
                payment.transaction_id = result['trans_id']
                payment.save()
                return Response({'order_number': payment.order_number, 'trans_id': payment.transaction_id})
            else:
                payment.status = Payment.FAILED
                # payment.response = result['error_message']
                payment.save()
                return Response({'error': 'error_message'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            payment.status = Payment.FAILED
            payment.response = 'An error occurred while processing the payment'
            payment.save()
            return Response({'error': 'An error occurred while processing the payment'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

class PaymentCallbackViewApiView(APIView):
    @extend_schema(
            request=serializers.PaymentApiViewSerializer,
    )
    @transaction.atomic
    def post(self, request):

        serializer = serializers.PaymentApiViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(
            Payment,
            order_number=serializer.validated_data["order_number"]
        )

        if USE_FAKE_PAYMENT:
            result = {
                "code": -1
            }
        else:
            result = {
                "code": 0
            }

        if result["code"] != -1:
            payment.status = Payment.FAILED
            payment.save()

            return Response(
                {"error": "Payment Failed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment.status == Payment.SUCCESS:
            return Response(
                {"success": "Payment already verified"}
            )

        payment.status = Payment.SUCCESS
        payment.save()

        wallet, _ = Wallet.objects.get_or_create(
            user=payment.user,
            defaults={"balance": 0}
        )

        wallet.balance += payment.amount
        wallet.save()

        cart = Cart.objects.get(
            user=payment.user,
            is_paid=False
        )

        payment_description = []
        error = False

        for cart_item in cart.cartitem.filter(on_deleted=False):

            menu = cart_item.menu

            if menu.number < cart_item.quantity:

                wallet.balance += cart_item.total_price
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    type="deposit",
                    amount=cart_item.total_price,
                )

                error = True
                continue

            payment_description.append({
                "menuid": menu.id,
                "order": cart_item.quantity,
                "price": cart_item.total_price,
            })

            menu.quantity += cart_item.quantity
            menu.number -= cart_item.quantity
            menu.save()

            cart_item.on_deleted = True
            cart_item.save()

        payment.description = payment_description
        payment.save()

        Transaction.objects.create(
            wallet=wallet,
            type="deposit",
            amount=payment.amount,
        )

        Transaction.objects.create(
            wallet=wallet,
            type="withdrawal",
            amount=payment.amount,
        )

        wallet.balance -= payment.amount
        wallet.save()

        if error:
            return Response({
                "warning": "برخی سفارش‌ها موجود نبودند و مبلغ آن‌ها به کیف پول بازگشت."
            })

        return Response({
            "success": "Payment completed successfully"
        })