from django import template
from ..models import *
from datetime import date


register=template.Library()

@register.simple_tag
def check_user_package(user_id,plan_id):
    user=Custom_user.objects.get(id=user_id)
    plan=Subscription_plan.objects.get(id=plan_id)
    check_plan=Subscription.objects.filter(user=user,plan=plan).count()
    
    if check_plan > 0 :
        return True
    else:
        return False
    
    
@register.simple_tag
def check_plan_Validity(user_id,plan_id):
    user=Custom_user.objects.get(id=user_id)
    plan=Subscription_plan.objects.get(id=plan_id)
    check_plan=Subscription.objects.filter(user=user,plan=plan).count()
    
    if check_plan > 0 :
        today=date.today()
        _plan=Subscription.objects.filter(user=user,plan=plan).order_by('-id').first()
        exp_date=_plan.end_date
        if exp_date > today:
            return True
        else :
            return False
    