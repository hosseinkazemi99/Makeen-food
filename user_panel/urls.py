from django.urls import path
from . import views 

app_name = 'user_panel'

urlpatterns = [
    path('menu-user/', views.ShowMenuApiView.as_view(), name='menu-user'),
    path('cart-user/', views.GetCartApiView.as_view(), name='get_cart-user'),
    path('create-cart-item/', views.CreateCartItemApiView.as_view(), name='create-cart-item-user'),
    path('show-order-user/', views.ShowOrderApiView.as_view(), name='show-order-user'),
    path('wallet-detail-user/', views.WalletDetailApiView.as_view(), name='wallet-detail-user'),
    path('all-cart-item-user/', views.ShowAllCartItemApiView.as_view(), name='show-all-cart-item-user'),
    path('cancel-cart-item-user/<int:pk>/', views.CancelCartItemApiView.as_view(), name='cancel_cart_item-user'),
    path('update-cart-item-user/<int:pk>/', views.UpdateCartItemApiView.as_view(), name='update_cart_item-user'),
    path('create-trans-id/',views.NextPayCreatePaymentApiView.as_view(), name='transid'),
    path('payment-callback/',views.PaymentCallbackViewApiView.as_view(), name='payment-callback'),
]
