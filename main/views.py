import json
import os
from django.conf import settings
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
import stripe
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.forms.utils import ErrorList
from django.contrib.auth import update_session_auth_hash
from django.core import serializers
from django.contrib.auth.decorators import user_passes_test
from time import time
from django.core.cache import cache
from django.contrib import messages



def trainer_required(function=None, redirect_field_name=None, login_url='login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and getattr(u, 'role', None) == 'trainer',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator







# Create your views here.
def home_view(request):
    plans=Subscription_plan.objects.all()
    services=Services.objects.all()
    trainers=Trainer.objects.all()
    banner=Banner.objects.all()
    return render(request,'home.html',{'data':services,'banners':banner,'plans':plans,'trainers':trainers})


def about_view(request):
    data=Gym_details.objects.first()
    trainers=Trainer.objects.all()
    return render(request,'about-us.html',{'data':data,'trainers':trainers})


def service_detail_view(request,id):
    services=Services.objects.all()
    service=Services.objects.get(id=id)
    return render(request,'service-detail.html',{'data':service,'services':services})


def services_view(request):
    services=Services.objects.all()
    return render(request,'services.html',{'data':services})


def teams_view(request):
    trainers=Trainer.objects.all()

    return render(request,'team.html',{'trainers':trainers})


def contact_view(request):
    form=Enquiry_form()
    contact=Gym_details.objects.first()
    return render(request,'contact.html',{'data':contact,'form':form})


def faq_view(request):
    faq=Faq.objects.all()
    return render(request,'faq.html',{'faq':faq})



def enquiry_view(request):
    if request.method == 'POST':
        form=Enquiry_form(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success':True,'message':'form submitted successfully'})
        else:
            return JsonResponse({'success':False,'errors':form.errors})
    return JsonResponse({'success':False,'message':'invalid request method'})



def Gallery_view(request):
    category=Gallery_category.objects.all()
    return render(request,'gallery.html',{'data':category})



def Gallery_detail_view(request,id):
    category=Gallery_category.objects.get(id=id)
    gallery=Gallery.objects.filter(category=id)
    return render(request,'gallery-details.html',{'data':gallery,'title':category.title})



def signup_view(request):
    if request.method=='POST':
        form=Signup_form(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return JsonResponse({'success':True,'redirect_url':'/'})
        else:
            errors=form.errors.as_json()
            return JsonResponse({'success':False,'errors':errors})

    else:
        form=Signup_form()
        return render(request,'registration/signup.html',{'form':form})
    
@login_required   
def Checkout(request,id):
  plan=Subscription_plan.objects.get(id=id)  
  return render(request,'checkout.html',{'plan':plan})

stripe.api_key = settings.STRIPE_SECRET_KEY   

@csrf_exempt
def checkout_session(request, id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            months = int(body.get("months", 1))
            total_amount = float(body.get("total_amount", 0.0))

            plan = Subscription_plan.objects.get(id=id)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"{plan.title} ({months} months)",
                            },
                            "unit_amount": int(float(total_amount) * 100),  # cents
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url='http://127.0.0.1:8000/payment_success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url="http://127.0.0.1:8000/payment_cancel",
                
                metadata={
                    "plan_id": plan.id,
                    "duration": months,
                    "price": total_amount,
                },
            )

            return JsonResponse({"url": session.url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)



def payment_success(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        return HttpResponse("❌ Missing session_id in the URL", status=400)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        metadata=session.metadata
        plan_id = metadata.plan_id
        plan=Subscription_plan.objects.get(id=plan_id)
        price=metadata.price
        duration = int(float(metadata.get("duration", 1)))
        start_date = datetime.today().date()
        end_date = start_date + relativedelta(months=duration)
        
        old_plan=Subscription.objects.get(user=request.user)
        if old_plan:
            old_plan.delete()
        
        Subscription.objects.create(
            user=request.user,
            plan=plan,
            duration_month=duration,
            total_amount=price,
            start_date=start_date,
            end_date=end_date
        )
        
        subject="Your Subscription Confirmation"
        from_email="mujeebrahmanikaynoor1234@gmail.com"
        to_email=request.user.email
        
        context = {
            'username':request.user.username,
            'plan':Subscription_plan.objects.get(id=plan_id),
            'price':metadata.price,
            'duration' : int(float(metadata.get("duration", 1))),
            'start_date' : datetime.today().date(),
            'end_date' : start_date + relativedelta(months=duration),
        }
        
        html_content= render_to_string('emails/subscription_mail.html',context)
        email=EmailMessage(subject,html_content,from_email,[to_email])
        email.content_subtype= "html"
        email.send()

        return render(request, 'success.html', {
            "plan_id": plan_id,
            "session": session
        })

    except stripe.error.InvalidRequestError:
        return HttpResponse("❌ Invalid session ID", status=404)
    except Exception as e:
        return HttpResponse(f"❌ Unexpected error: {str(e)}", status=500) 


def payment_cancel(request):
    return render(request,'cancel.html') 

@login_required
def user_dashboard_view(request):
    user=request.user
    plan=Subscription.objects.get(user=user)
    today=date.today()
    status=0
    if plan.end_date > today:
        status=1
    subscriber=Subscriber.objects.get(user=user)
    a_trainer=Asign_trainer.objects.get(subscriber=subscriber)
    achievment=Trainer_achievments.objects.filter(trainer=a_trainer.trainer)
    
    data=Notification.objects.filter(status=True).order_by('-id')
    unread=0
    for i in data:
        status_data=Notification_user_status.objects.filter(user=request.user,notification=i).first()
        if status_data:
            unread=0
        else:
            unread=unread+1
  
    return render(request,'user/user-dashboard.html',{'user':user,'cplan':plan,'a_trainer':a_trainer,'unread':unread,'achievment':achievment,'status':status})

@login_required
def user_profile_view(request):
    if request.method=='POST':
        form=Profile_change_form(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            updated_html=render_to_string('partials/updated_profile_form.html',{'form':Profile_change_form(instance=request.user)},request=request)
            return JsonResponse({'html':updated_html,'status':'success'})
        else:
            return JsonResponse({'error':'Update Failed'},status=400)
    else: 
        form=Profile_change_form(instance=request.user)
        
        data=Notification.objects.filter(status=True).order_by('-id')
        unread=0
        for i in data:
            status_data=Notification_user_status.objects.filter(user=request.user,notification=i).first()
            if status_data:
                unread=0
            else:
                unread=unread+1
  
        
        return render(request,'user/user-profile.html',{'form':form,'unread':unread})
    
@login_required   
def user_change_password_view(request):
    if request.method=='POST':
        form=Password_Change_Form(data=request.POST,user=request.user)
        print(request.POST)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, user)
            updated_html=render_to_string('partials/user_updated_change_password.html',{'form':Password_Change_Form(user=request.user)},request=request)
            return JsonResponse({'html':updated_html,'status':'success'})
        else:
            print(form.errors)
            error_dict = {}
            for field, errors in form.errors.items():
                error_dict[field] = errors
                
            return JsonResponse({'success':False,'errors':error_dict},status=400)
    else:
        form=Password_Change_Form(user=request.user)
        
        data=Notification.objects.filter(status=True).order_by('-id')
        unread=0
        for i in data:
            status_data=Notification_user_status.objects.filter(user=request.user,notification=i).first()
            if status_data:
                unread=0
            else:
                unread=unread+1
        
        return render(request,'user/user-change-password.html',{'form':form,'unread':unread})
    
    
def notification_view(request):
    data=Notification.objects.filter(status=True).order_by('-id')
    return render(request,'notifications.html',{'data':data})

def fetch_notification_view(request):
    data=Notification.objects.filter(status=True).order_by('-id')
    json_data=[]
    unread=0
    status=False
    for i in data:
        status_data=Notification_user_status.objects.filter(user=request.user,notification=i).first()
        if status_data:
            status=True
            json_data.append({
                'pk':i.id,
                'content':i.content,
                'created_date':i.created_date,
                'status':status
            })
        else:
            status=False
            unread=unread+1
            json_data.append({
                'pk':i.id,
                'content':i.content,
                'created_date':i.created_date,
                'status':status
            })
        
    return JsonResponse({'data':json_data,'unread':unread})

@login_required
def mark_read_view(request):
    not_id=request.GET['notification']
    data=Notification.objects.get(id=not_id)
    user=request.user
    Notification_user_status.objects.create(notification=data,user=user)
    readed=Notification_user_status.objects.filter(user=request.user).values_list('notification_id',flat=True)
    unread=Notification.objects.exclude(id__in=readed).count()
    
    
    return JsonResponse({'bool':True,'unread':unread,'data': {
        'id': data.id,
        'content': data.content,
        'created_date': data.created_date.strftime('%B %d, %Y').replace(' 0', ' ')
    }})


@trainer_required
def trainer_dashboard_view(request):
    key=f"salary_notification{request.user.id}"
    msg=cache.get(key)
    if msg:
        messages.success(request,msg)
        cache.delete(key)
        
    key=f"assign_notification{request.user.id}"
    msg=cache.get(key)
    if msg:
        messages.success(request,msg)
        cache.delete(key)
        
    trainer=request.user
    return render(request,'trainer/dashboard.html',{'trainer':trainer})
    
    
    
@trainer_required
def trainer_profile_view(request):
    if request.method=='POST':
        trainer=Trainer.objects.get(trainer=request.user)
        form=Trainer_profile_form(request.POST,request.FILES,instance=trainer,user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            trainer=Trainer.objects.get(trainer=request.user)
            if trainer.image.url:
                updated_html=render_to_string('partials/trainer-updated-profile.html',{'form':Trainer_profile_form(instance=trainer,user=request.user),'image':trainer.image.url,},request=request)
                return JsonResponse({'html':updated_html,'status':'success','image':trainer.image.url,})
            else:
                updated_html=render_to_string('partials/trainer-updated-profile.html',{'form':Trainer_profile_form(instance=trainer,user=request.user),'image':trainer.image,},request=request)
                return JsonResponse({'html':updated_html,'status':'success','image':trainer.image,})

        else:
            return JsonResponse({'error':'Update Failed'},status=400)
    else: 
        trainer=Trainer.objects.get(trainer=request.user)
        form=Trainer_profile_form(instance=trainer,user=request.user)
        
        data=Notification.objects.filter(status=True).order_by('-id')
        unread=0
        for i in data:
            status_data=Notification_user_status.objects.filter(user=request.user,notification=i).first()
            if status_data:
                unread=0
            else:
                unread=unread+1
  
        trainer=Trainer.objects.get(trainer=request.user)
        return render(request,'trainer/trainer-profile.html',{'form':form,'unread':unread,'image':trainer.image})
    
    
    
@trainer_required
def Subscribers_view(request):
    trainer=Trainer.objects.get(trainer=request.user)
    subscribers=Asign_trainer.objects.filter(trainer=trainer)
    return render(request,'trainer/subscribers.html',{'data':subscribers})


@trainer_required
def Payments_view(request):
    trainer=Trainer.objects.get(trainer=request.user)
    payment=Monthly_salary.objects.filter(trainer=trainer).order_by('-id')
    return render(request,'trainer/payments.html',{'data':payment})



@trainer_required   
def trainer_change_password_view(request):
    if request.method=='POST':
        form=Password_Change_Form(data=request.POST,user=request.user)
        print(request.POST)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, user)
            updated_html=render_to_string('partials/user_updated_change_password.html',{'form':Password_Change_Form(user=request.user)},request=request)
            return JsonResponse({'html':updated_html,'status':'success'})
        else:
            print(form.errors)
            error_dict = {}
            for field, errors in form.errors.items():
                error_dict[field] = errors
                
            return JsonResponse({'success':False,'errors':error_dict},status=400)
    else:
        form=Password_Change_Form(user=request.user)
        
        data=Notification.objects.filter(status=True).order_by('-id')
        unread=0
        for i in data:
            status_data=Notification_user_status.objects.filter(user=request.user,notification=i).first()
            if status_data:
                unread=0
            else:
                unread=unread+1
        
        return render(request,'trainer/tainer-change-password.html',{'form':form,'unread':unread})
    
    
@trainer_required   
def trainer_notification_view(request):
    data=Notification.objects.filter(status=True).order_by('-id')
    json_data=[]
    unread=0
    status=False
    for i in data:
        status_data=Notification_user_status.objects.filter(user=request.user,notification=i).first()
        if status_data:
            status=True
            json_data.append({
                'id':i.id,
                'message':i.content,
                'date':i.created_date,
                'status':status
            })
        else:
            status=False
            unread=unread+1
            json_data.append({
                'id':i.id,
                'message':i.content,
                'date':i.created_date,
                'status':status
            })
    return render(request,'trainer/notifications.html',{'data':json_data,'unread':unread})