from app.common import get_db
from django.conf import settings
from rest_framework.decorators import api_view
from django.http import HttpResponse
from app.common import twilio_client
from twilio.twiml.voice_response import VoiceResponse
from rest_framework.response import Response

@api_view(['POST'])
def incoming(request):
    response = VoiceResponse()
    data = request.data
    if not len(list(get_db().Calls.find({"call_sid":data.get("CallSid")}))):
        get_db().Calls.insert_one({'from_number':data.get("From"),'to_number': data.get("To"), 'call_sid':data.get("CallSid")})
    connect = response.connect()
    connect.stream(url=f'wss://{settings.APP_URL}/ws/connection/')
    return HttpResponse(str(response))

@api_view(['POST'])
def outgoing(request):
    client = twilio_client()
    phone = request.data['phone']
    call = client.calls.create(
        url=f'https://{settings.APP_URL}/incoming-call/',
        to=phone,
        from_=settings.TWILIO_NUMBER
        )
    get_db().Calls.insert_one({ "call_sid": call.sid, "from_number": settings.TWILIO_NUMBER, "to_number": phone})
    return Response({'message':call.sid})

def get_date_of_current_week(day):
    from datetime import datetime, timedelta

    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    input_day = day.lower()

    if input_day not in days_of_week:
        return 'Invalid day input. Please enter a valid day of the week.'

    current_date = datetime.now()
    current_day_index = current_date.weekday()
    target_day_index = days_of_week.index(input_day)
    days_until_target_day = (target_day_index - current_day_index + 7) % 7

    target_date = current_date + timedelta(days=days_until_target_day)

    return target_date