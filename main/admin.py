from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.admin import UserAdmin



# Register your models here.
admin.site.register(Services)


class Achievements_inline(admin.TabularInline):
    model=Trainer_achievments
    extra=4
    min_num=1
    can_delete=True


class Trainer_admin(admin.ModelAdmin):
    list_display=('trainer','get_email','salary','profession','address')
    inlines=[Achievements_inline]
    
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('trainer', 'profession', 'address', 'image',),
        }),
    )

    fieldsets = (
        (None, {'fields': ('trainer', 'profession','address','image')}),
        ('Social Links', {'fields': ('whatsapp', 'facebook', 'linkedin','instagram','youtube')}),
        ('Salary', {'fields': ('salary',)}),
    )
    
    def get_email(self, obj):
        return obj.trainer.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'trainer__email'
    
    
    
admin.site.register(Trainer,Trainer_admin)

class User_admin(UserAdmin):
    list_display=['username','email','role']
    
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name','role'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password','role')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    

admin.site.register(Custom_user,User_admin)


    
    
class Singleitem_contact(admin.ModelAdmin):
    
    list_display=['image_tag','phone','email','address','whatsapp_no']
    
    def has_add_permission(self, request):
        return not Gym_details.objects.exists()
    
    def has_delete_permission(self, request, obj = None):
        return False
    

admin.site.register(Gym_details,Singleitem_contact)
admin.site.register(Faq)

class Banner_admin(admin.ModelAdmin):
    list_display=('alt_text','image_tag')


admin.site.register(Banner,Banner_admin)

class Enquiry_admin(admin.ModelAdmin):
    list_display=('email','name','phone','message')
admin.site.register(Enquiry,Enquiry_admin)


class Gallery_inline(admin.TabularInline):
    model= Gallery
    extra= 3
    min_num= 1
    can_delete= True

class Category_admin(admin.ModelAdmin):
    inlines=[Gallery_inline]
    list_display=('title','image_tag')
    
    def __str__(self):
        return Gallery


admin.site.register(Gallery_category,Category_admin)




class Subscription_inline(admin.TabularInline):
    model= Subscription_feature
    extra= 5
    min_num= 1
    can_delete= True
    
    
class Discount_inline(admin.TabularInline):
    model= Plan_discount
    extra= 3
    min_num= 1
    can_delete= True
    
class Subscription_admin(admin.ModelAdmin):
    inlines=[Subscription_inline,Discount_inline]
    list_display = ['title', 'price', 'get_features']

    def get_features(self, obj):
        return ", ".join([f.feature for f in obj.subscription_feature_set.all()])
    get_features.short_description = 'Features' 

    # Column header name
    
admin.site.register(Subscription_plan,Subscription_admin)




class Subscription_admin(admin.ModelAdmin):
    list_display=['user','plan','duration_month','total_amount','start_date','end_date']
    
admin.site.register(Subscription,Subscription_admin)


class Subscriber_admin(admin.ModelAdmin):
    list_display=['user','address','phone']
    
admin.site.register(Subscriber,Subscriber_admin)


class Notification_admin(admin.ModelAdmin):
    list_display=['content','created_date','status']
    list_editable=['status']
    
admin.site.register(Notification,Notification_admin)

class Notification_read_status_admin(admin.ModelAdmin):
    list_display=['notification','user']
    
admin.site.register(Notification_user_status,Notification_read_status_admin)



class Assign_trainer_admin(admin.ModelAdmin):
    list_display=['trainer','subscriber']
    
admin.site.register(Asign_trainer,Assign_trainer_admin)



class Salary_admin(admin.ModelAdmin):
    list_display=['trainer','month','year','worked_days','amount','added_date']
    
admin.site.register(Monthly_salary,Salary_admin)