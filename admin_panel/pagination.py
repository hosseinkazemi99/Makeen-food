from rest_framework.pagination import PageNumberPagination


class OrderReportPagination(PageNumberPagination):
    page_size = 7

class AllUsersPagination(PageNumberPagination):
    page_size = 10

class AllFoodsPagination(PageNumberPagination):
    page_size = 5