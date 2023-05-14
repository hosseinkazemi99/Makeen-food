from django.urls import path
from .views import LoginPanel, CreateUser, OrderReport, FinancialReport, Users, DeleteUser, CreateFood, Foods,DeleteFood,UpdateFood,CreateMenu,DeleteMenu, AdminUser

app_name = 'admin_panel'
urlpatterns = [
    path('login/', LoginPanel.as_view(), name='login_admin'),
    path('create-admin/', AdminUser.as_view(), name='create_admin'),
    path('create-user/', CreateUser.as_view(), name='create_user'),
    path('order-report/', OrderReport.as_view(), name='order_report'),
    path('financial-Report/', FinancialReport.as_view(), name='Financial_Report'),
    path('users/', Users.as_view(), name='users'),
    path('create-food/', CreateFood.as_view(), name='create_food'),
    path('foods/', Foods.as_view(), name='foods'),
    path('delete-user/<int:id>/', DeleteUser.as_view(), name='delete_user'),
    path('delete-food/<int:id>/', DeleteFood.as_view(), name='delete_foods'),
    path('delete-menu/<int:id>/', DeleteMenu.as_view(), name='delete_menu'),
    path('update-food/<int:id>/', UpdateFood.as_view(), name='update_foods'),
    path('create-menu/', CreateMenu.as_view(), name='create-menu'),
]
