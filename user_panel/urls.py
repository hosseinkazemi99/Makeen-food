from django.urls import path
from .views import LoginUser, ShowMenu, GetCart, CreateCartItem, WalletDetail, ShowAllCartItem, CancleCartItem, \
    UpdateCartItem, NextPayCreatePayment,PaymentCallbackView, ShowOrder

app_name = 'user_panel'

urlpatterns = [
    path('login-user/', LoginUser.as_view(), name='loginuser'),
    path('menu-user/', ShowMenu.as_view(), name='menu-user'),
    path('cart-user/', GetCart.as_view(), name='get_cart-user'),
    path('create-cartitem/', CreateCartItem.as_view(), name='createcartitem-user'),
    path('show-order-user/', ShowOrder.as_view(), name='show-order-user'),
    path('walletdetail-user/', WalletDetail.as_view(), name='walletdetail-user'),
    path('allcartitem-user/', ShowAllCartItem.as_view(), name='showallcartitem-user'),
    path('canclecartitem-user/<int:id>/', CancleCartItem.as_view(), name='canclecartitem-user'),
    path('updatecartitem-user/<int:id>/', UpdateCartItem.as_view(), name='updatecartitem-user'),
    path('createtransid/',NextPayCreatePayment.as_view(), name='transid'),
    path('peymentcallback/',PaymentCallbackView.as_view(), name='paymentcallback'),
]
