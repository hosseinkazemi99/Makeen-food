from django.urls import path
from . import views
app_name = 'admin_panel'
urlpatterns = [
    path('login/', views.LoginPanelApiView.as_view(), name='login_admin'),
    path('create-user/', views.CreateUserApiView.as_view(), name='create_user'),
    path('users/', views.AllUsersApiView.as_view(), name='users'),
    path('create-admin/', views.CreateAdminApiView.as_view(), name='create_admin'),
    path('foods/', views.AllFoodsApiView.as_view(), name='foods'),
    path('order-report/', views.OrderReportApiView.as_view(), name='order_report'),
    path('financial-Report/', views.FinancialReportApiView.as_view(), name='Financial_Report'),
    path('delete-user/<int:pk>/', views.DeleteUserApiView.as_view(), name='delete_user'),
    path('create-food/', views.CreateFoodApiView.as_view(), name='create_food'),
    path('delete-food/<int:pk>/', views.DeleteFoodApiView.as_view(), name='delete_foods'),
    path('update-food/<int:pk>/', views.UpdateFoodApiView.as_view(), name='update_foods'),
    path('create-menu/', views.CreateMenuApiView.as_view(), name='create-menu'),
    path('delete-menu/<int:pk>/', views.DeleteMenuApiView.as_view(), name='delete_menu'),
]

