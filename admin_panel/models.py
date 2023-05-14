from django.db import models


# class Rank(models.Model):
#     name = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     modify_at = models.DateTimeField(auto_now=True)
#     on_deleted = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f'{self.name}'


# class Package(models.Model):
#     name = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     modify_at = models.DateTimeField(auto_now=True)
#     on_deleted = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f'{self.name}'




class Food(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField()
    created_at = models.DateField(auto_now_add=True)
    modify_at = models.DateField(auto_now=True)
    on_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name




class MenuModel(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    day_of_week = models.CharField(max_length=15, editable=False)
    number = models.PositiveSmallIntegerField(default=50)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    modify_at = models.DateField(auto_now=True)
    on_deleted = models.BooleanField(default=False)


    @property
    def image(self):
        return self.food.image.url

    @property
    def price(self):
        return self.food.price

    def save(self, *args, **kwargs):
        self.day_of_week = self.date.strftime('%A')
        super(MenuModel, self).save(*args, **kwargs)

    def __str__(self):
        return f' تاریخ {self.date} '
