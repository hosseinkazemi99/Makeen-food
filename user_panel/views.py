import datetime
from rest_framework import status
from rest_framework.response import Response
from .permissions import IsUserOrReadOnly
from rest_framework.permissions import IsAuthenticated
from admin_panel.models import MenuModel
from rest_framework.views import APIView
from .serializers import LoginUserSerializer, ShowMenuSerializer, GetCartSerializer, CreateCartItemSerializer, \
    CartItemSerializer, WalletSerializer, ShowAllCartItemSerializer, UpdateCartItemSerializer, PaymentSerializer, \
    ShowOrderSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CartItem, Cart, UserModel, Wallet, Payment, Transaction

import os
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
import requests
from django.db import transaction


class LoginUser(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = UserModel.objects.get(username=username, password=password)

        refresh = RefreshToken.for_user(user)
        response_data = {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }

        return Response(data=response_data, status=status.HTTP_200_OK)


class ShowMenu(APIView):
    permission_classes = [IsAuthenticated, IsUserOrReadOnly]

    def get(self, request):
        menus = MenuModel.objects.filter(date__gte=datetime.date.today(), on_deleted=False)
        serializer = ShowMenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShowOrder(APIView):
    permission_classes = [IsAuthenticated, IsUserOrReadOnly]

    def get(self, request):
        cart_items = CartItem.objects.filter(menu__date__gte=datetime.date.today(), cart__user=request.user,
                                             on_deleted=True)
        serializer = ShowOrderSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCart(APIView):
    permission_classes = [IsAuthenticated, IsUserOrReadOnly]

    def get(self, request):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
        if created:
            cart = created

        serializer = GetCartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateCartItem(APIView):
    permission_classes = [IsAuthenticated, IsUserOrReadOnly]

    def post(self, request):
        serializer = CreateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menu_id = serializer.validated_data['menu_id']
        quantity = serializer.validated_data['quantity']
        menu = MenuModel.objects.get(id=menu_id)
        cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
        cart_item = CartItem.objects.create(cart=cart, menu=menu, price=menu.price, quantity=quantity)
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShowAllCartItem(APIView):
    permission_classes = [IsUserOrReadOnly]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user, is_paid=False)
        except Cart.DoesNotExist:
            return Response({'detail': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = cart.cartitem.filter(on_deleted=False)
        serializer = ShowAllCartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateCartItem(APIView):
    permission_classes = [IsUserOrReadOnly]

    def put(self, request, id):
        try:
            cart_item = CartItem.objects.get(id=id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CancleCartItem(APIView):
    permission_classes = [IsUserOrReadOnly]

    def delete(self, request, id):
        try:
            cart_item = CartItem.objects.get(id=id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WalletDetail(APIView):
    permission_classes = [IsUserOrReadOnly]

    def get(self, request):
        user = request.user
        wallet_exists = Wallet.objects.filter(user=user).exists()
        if wallet_exists:
            wallet = Wallet.objects.get(user=user)
            transactions = wallet.transactions.all()
            serializer = WalletSerializer({'wallet': wallet, 'transactions': transactions})
            return Response(serializer.data)
        else:
            return Response({'wallet': ' your wallet is empty'})


###########################
class NextPayCreatePayment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        last_order = Payment.objects.filter().order_by('-id')[:1].get()
        if last_order:
            order = (last_order.order_number + 1)
        else:
            order = 1000000
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


class PaymentCallbackView(APIView):

    @transaction.atomic
    def post(self, request, format=None):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data['order_number']
        # چک کردن وضعیت پرداخت
        url = 'https://nextpay.org/nx/gateway/verify'
        payment = Payment.objects.filter(order_number=order_number).exists()
        if not payment:
            return Response({"ordernumber": "does not exist"})
        payment = Payment.objects.get(order_number=order_number)
        user = payment.user
        MainAmountInt = payment.amount
        trans_id = payment.transaction_id
        data = {
            'api_key': os.environ.get('PEYMENT-KEY'),
            'trans_id': trans_id,
            'amount': MainAmountInt
        }
        headers = {
            'User-Agent': 'PostmanRuntime/7.26.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, headers=headers, data=data)
        print(response.json())
        result = response.json()
        if response.status_code == status.HTTP_200_OK:

            result = response.json()

            if result['code'] == -1:

                # پرداخت با موفقیت انجام شده

                # آپدیت وضعیت پرداخت در دیتابیس
                # payment = Payment.objects.get(id=result['order_id'])
                if payment.status == Payment.PENDING:

                    payment.status = Payment.SUCCESS
                    payment.save()

                    # اضافه کردن مبلغ پرداخت شده به کیف پول کاربر
                    wallet = Wallet.objects.filter(user=payment.user).exists()
                    if not wallet:
                        Wallet.objects.create(user=payment.user, balance=0)
                    wallet = Wallet.objects.get(user=payment.user)
                    wallet.balance += payment.amount
                    wallet.save()
                    # بروزرسانی منو
                    cart = Cart.objects.get(user=payment.user, is_paid=False)
                    cart_items = cart.cartitem.filter(on_deleted=False)
                    payment_description = []
                    error = False
                    for cart_item in cart_items:
                        menu = cart_item.menu

                        if menu.number - cart_item.quantity < 0:
                            userwallet = Wallet.objects.get(user=payment.user)
                            userwallet.balance += cart_item.total_price
                            deposit = Transaction.objects.create(wallet=wallet, type='deposit',
                                                                 amount=cart_item.total_price)
                            error = True
                            userwallet.save()
                            deposit.save()
                        else:
                            menuid = menu.id
                            order = cart_item.quantity
                            price = cart_item.total_price
                            lst = {'menuid': menuid, 'order': order, 'price': price}
                            payment_description.append(lst)
                            cart_item.on_deleted = True
                            menu.quantity += cart_item.quantity
                            menu.number -= cart_item.quantity
                            menu.save()
                            cart_item.save()
                    payment.description = payment_description
                    payment.save()
                    # بروزرسانی کیف پول

                    wallet = Wallet.objects.get(user=payment.user)
                    deposit = Transaction.objects.create(wallet=wallet, type='deposit', amount=MainAmountInt)
                    whithdrawal = Transaction.objects.create(wallet=wallet, type='withdrawal', amount=MainAmountInt)
                    wallet.balance -= MainAmountInt
                    wallet.save()
                    deposit.save()
                    whithdrawal.save()
                    if error:
                        return Response(
                            {"خطا": "متاسفانه برخی از سفارشات شما انجام نشد هزینه واریزی به کیف پول شما واریز شد"})

                    return Response({'success': 'Payment completed successfully'})
                else:
                    return Response({'success': 'Payment already verified'})

            else:
                # خطایی در پرداخت رخ داده
                # payment = Payment.objects.get(id=result['order_id'])
                payment.status = Payment.FAILED
                payment.save()
                return Response({'error': 'error_message'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            # خطایی در برقراری ارتباط با درگاه پرداخت رخ داده
            # payment = Payment.objects.get(id=result['order_id'])
            payment.status = Payment.FAILED
            payment.response = 'An error occurred while verifying the payment'
            payment.save()
            return Response({'error': 'An error occurred while verifying the payment'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
