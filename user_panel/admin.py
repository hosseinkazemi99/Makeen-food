from django.contrib import admin
from .models import UserModel, Cart, CartItem, Wallet, Transaction, Payment
admin.site.register(UserModel)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Payment)