from .models import Gym_details

def contact_context(request):
    try:
        contact=Gym_details.objects.first()
    except Gym_details.DoesNotExist:
        contact=None
    return {'contact':contact}