from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from admin_panel.models import MenuModel
from django.db import models


class UserModelManager(BaseUserManager):
    def create_user(self, username, password=None):

        if not username:
            raise ValueError("Users must have an email address")

        else:
            user = self.model(username=username)
            user.set_password(password)
            user.save()
            return user

    def create_superuser(self, username, password):

        user = self.create_user(username, password=password, )
        user.is_staff = True
        user.is_admin = True
        user.save()
        return user


class UserModel(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True, )
    name = models.CharField(max_length=100)
    # rank = models.ForeignKey(Rank, on_delete=models.PROTECT, null=True)
    rank = models.CharField(max_length=50, null=True)
    # package = models.ForeignKey(Package, on_delete=models.PROTECT, null=True)
    package = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    on_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modify_at = models.DateTimeField(auto_now=True)
    objects = UserModelManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["password"]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Cart(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modify_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def total_price(self):
        total = 0
        for cart_item in self.cartitem.filter(on_deleted=False):
            total += (cart_item.price * cart_item.quantity)
        return int(total)

    def __str__(self):
        return f'{self.id}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitem')
    menu = models.ForeignKey(MenuModel, on_delete=models.CASCADE, related_name='menu')
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveSmallIntegerField(default=0)
    on_deleted = models.BooleanField(default=False)

    @property
    def total_price(self):
        return int(self.price * self.quantity)

    def __str__(self):
        return f'{self.id}'


class Wallet(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'deposit'),
        ('withdrawal', 'withdrawal'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.username} -{self.type} - {self.amount} - {self.timestamp}"


class Payment(models.Model):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    )

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=50, null=True)
    order_number=models.BigIntegerField(default=1000000)
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()
    description = models.TextField(null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    # token = models.CharField(max_length=100, blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    # timestamp = models.DateTimeField(auto_now_add=True)
    create_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order{self.order_number} - User{self.user.username}, amount {self.amount}'
