from django.db import models

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
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True)
    price = models.IntegerField(editable=False)
    date = models.DateField()
    day_of_week = models.CharField(max_length=15, editable=False)
    number = models.PositiveSmallIntegerField(default=50)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    modify_at = models.DateField(auto_now=True)
    on_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.day_of_week = self.date.strftime('%A')
        if self.pk:
            original = MenuModel.objects.get(pk=self.pk)
            self.price = original.price
        elif self.food:
            self.price = self.food.price
        super(MenuModel, self).save(*args, **kwargs)

    def __str__(self):
        return f' تاریخ {self.date} '
