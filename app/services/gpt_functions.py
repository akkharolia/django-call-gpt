import json
from app.views import get_date_of_current_week
from app.common import get_db


def appointment_booking(args):
    args = json.loads(args)
    day = get_date_of_current_week(args.get('day'))
    get_db().Appointment.insert_one({'callSid':args.get('call_sid'), 'date':day, 'time':args.get('time')})
    return "Appointment saved successfully. End the call."

def save_customer_details(args):
    args = json.loads(args)
    get_db().Calls.find_one_and_update({'call_sid':args.get('call_sid')}, {"$set":{"full_name":args.get('full_name')}})
    return "Customer details saved successfully. Assist customer for the plans."

def end_call(args):
    return "End the call"