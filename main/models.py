from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import User,AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from django.utils.timezone import now
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json




class Custom_user(AbstractUser):
    ROLES=(
        ('user','User'),
        ('trainer','Trainer'),
    )
    
    role=models.CharField(max_length=20,choices=ROLES,default='user')
    
    



# Create your models here.
class Services(models.Model):
    title=models.CharField(max_length=100)
    description=models.TextField()
    image=models.ImageField(upload_to='service_images')
    
    def __str__(self):
        return self.title
    
    


class Trainer(models.Model):
    trainer=models.ForeignKey(Custom_user,on_delete=models.CASCADE)
    profession=models.CharField(max_length=100,null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    image=models.ImageField(upload_to="trainer_images",null=True,blank=True)
    facebook=models.CharField(max_length=200,null=True,blank=True)
    whatsapp=models.CharField(max_length=200,null=True,blank=True)
    instagram=models.CharField(max_length=200,null=True,blank=True)
    linkedin=models.CharField(max_length=200,null=True,blank=True)
    youtube=models.CharField(max_length=200,null=True,blank=True)
    salary=models.IntegerField(default=0)




    
    
    def __str__(self):
        return self.trainer.username
 
    
    
@receiver(post_save,sender=Custom_user)
def create_trainer(sender,instance,created,**kwargs):
    if instance.role=='trainer':
        Trainer.objects.get_or_create(trainer=instance)
    else:
        Trainer.objects.filter(trainer=instance).delete()
    
class Gym_details(models.Model):
    logo=models.ImageField(upload_to='logo')
    phone=models.BigIntegerField()
    email=models.EmailField()
    address=models.CharField(max_length=200)
    map_location=models.TextField()
    about_gym=models.TextField()
    whatsapp_no=models.CharField(max_length=200)
    instagram_link=models.CharField(max_length=200)
    facebook_link=models.CharField(max_length=200)
    twitter_link=models.CharField(max_length=200)
    youtube_link=models.CharField(max_length=200)


    def image_tag(self):
        if self.logo:
            return mark_safe('<img src="%s" width="100">' %(self.logo.url))
        else:
            return 'No Logo'



    
    
class Banner(models.Model):
    image=models.ImageField(upload_to="banners")
    alt_text=models.CharField(max_length=100)
    content=models.TextField()
    
    def __str__(self):
        return self.alt_text
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="100">' %(self.image.url))
    
    

class Faq(models.Model):
    question=models.CharField(max_length=200)
    answer=models.TextField()
    
    def __str__(self):
        return self.question
    
    
class Enquiry(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.BigIntegerField()
    message=models.TextField()
    
    
    def __str__(self):
        return self.email
    
    
    
    
class Gallery_category(models.Model):
    title=models.CharField(max_length=100)
    cover_image=models.ImageField(upload_to='gallery_cover')
    
    def __str__(self):
        return self.title
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="100">' %(self.cover_image.url))
    
    class Meta:
        verbose_name="Gallery"

    
    
    
    
class Gallery(models.Model):
    category=models.ForeignKey(Gallery_category,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='gallery')
    alt_text=models.CharField(max_length=100)
    
    def __str__(self):
        return self.category.title
    
    def image_tag(self):
        return mark_safe('<img src="%s" width="100">' %(self.image.url))
    
    
    

    
    
    
class Subscription_plan(models.Model):
    title=models.CharField(max_length=200)
    price=models.IntegerField()
    
    def __str__(self):
        return self.title
    
    
    
class Subscription_feature(models.Model):
    plan=models.ForeignKey(Subscription_plan,on_delete=models.CASCADE)
    feature=models.CharField(max_length=300)
    
    def __str__(self):
        return self.plan.title
    
    
class Plan_discount(models.Model):
    plan=models.ForeignKey(Subscription_plan,on_delete=models.CASCADE)
    duration_months=models.IntegerField()
    discount=models.IntegerField()
    
    def __str__(self):
        return self.plan.title
    
    
class Subscription(models.Model):
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE)
    plan=models.ForeignKey(Subscription_plan,on_delete=models.CASCADE)
    duration_month=models.IntegerField()
    start_date=models.DateField(auto_created=True)
    end_date=models.DateField()
    total_amount=models.FloatField()
    
    def __str__(self):
        return self.user.username
    
 
class Subscriber(models.Model):
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE)
    address=models.CharField(max_length=200,null=True,blank=True)
    phone=models.IntegerField(null=True,blank=True)
    image=models.ImageField(upload_to='subscribers',null=True,blank=True)
    
    def __str__(self):
        return self.user.username
    
    
@receiver(post_save,sender=Custom_user)
def create_subscriber(sender,instance,created,**kwargs):
    if instance.role=='user':
        Subscriber.objects.get_or_create(user=instance)
    else:
        Subscriber.objects.filter(user=instance).delete()
        
        
        

class Notification(models.Model):
    content=models.TextField()
    read_by_user=models.ForeignKey(Subscriber,on_delete=models.CASCADE,null=True,blank=True)
    read_by_trainer=models.ForeignKey(Trainer,on_delete=models.CASCADE,null=True,blank=True)
    created_date=models.DateField(auto_now=True)
    status=models.BooleanField(default=True)
    
    
    def __str__(self):
        return self.content
    
    
@receiver(post_save,sender=Notification)
def notification_created(sender,instance,created,**kwargs):
    if created:
        channel_layer=get_channel_layer()
        total=Notification.objects.all().count()
        formatted_date = instance.created_date.strftime("%B %d, %Y").replace(" 0", " ")
        async_to_sync(channel_layer.group_send)(
            'notification',
            {'type':'send_notification',
             'message':instance.content,
             'id':instance.id,
             'date':formatted_date,
             'total':total}
        )
    
class Notification_user_status(models.Model):
    notification=models.ForeignKey(Notification,on_delete=models.CASCADE)
    user=models.ForeignKey(Custom_user,on_delete=models.CASCADE)
    
    
class Asign_trainer(models.Model):
    subscriber=models.ForeignKey(Subscriber,on_delete=models.CASCADE)
    trainer=models.ForeignKey(Trainer,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.trainer.trainer.username
    
    
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['trainer','subscriber'],name='unique_trainer_subscriber')
        ]
    
    
@receiver(post_save,sender=Asign_trainer)
def client_assign_created(sender,instance,created,**kwargs):
    if created:
        trainer_user=instance.trainer.trainer
        key=f"assign_notification{trainer_user.id}"
        added_date = now().strftime('%d %B %Y')
        msg = f"New Client {instance.subscriber.user.first_name} {instance.subscriber.user.last_name} is Assigned on {added_date}"
        cache.set(key,msg,timeout=86400)

    
    
class Trainer_achievments(models.Model):
    trainer=models.ForeignKey(Trainer,on_delete=models.CASCADE)
    achievment=models.CharField(max_length=300)
    description=models.TextField(null=True,blank=True)
    image=models.ImageField(upload_to='trainer_achievement',null=True,blank=True)
    
    


CURRENT_YEAR = datetime.datetime.now().year

def current_year():
    return datetime.datetime.now().year
    
    
class Monthly_salary(models.Model):
    MONTH_CHOICES = (
    ('january', 'January'),
    ('february', 'February'),
    ('march', 'March'),
    ('april', 'April'),
    ('may', 'May'),
    ('june', 'June'),
    ('july', 'July'),
    ('august', 'August'),
    ('september', 'September'),
    ('october', 'October'),
    ('november', 'November'),
    ('december', 'December'),
    )
    trainer=models.ForeignKey(Trainer,on_delete=models.CASCADE)
    month=models.CharField(choices=MONTH_CHOICES,max_length=100)
    year=models.IntegerField(default=current_year)
    worked_days=models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(30)
        ]
    )
    amount=models.BigIntegerField()
    added_date=models.DateField()
    
    
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['trainer','month','year'],name='unique_user_month_year')
        ]
        
        
@receiver(post_save,sender=Monthly_salary)
def notify_trainer_salary_created(sender,instance,created,**kwargs):
    if created:
        trainer_user=instance.trainer.trainer
        key=f"salary_notification{trainer_user.id}"
        added_date = now().strftime('%d %B %Y')
        msg = f"Salary of Rs.{instance.amount} For {instance.month.capitalize()} {instance.year} Was Added on {added_date}"
        cache.set(key,msg,timeout=86400)

    

    
    
    

        
        
        
    
    

    
    