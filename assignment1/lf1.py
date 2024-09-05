import os
import boto3
from datetime import datetime
from dateutil import parser
import logging
import re
import time

sqs = boto3.client('sqs')
queue_url = os.environ['SQS_URL']

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

_RE_WHITESPACE = re.compile(r"\s+")

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def proc_cuisine_str(cuisine: str) -> str:
    """
    Paraphrase cuisine so that it can match records in OpenSearch.
    """
    cuisine = cuisine.lower().replace('cuisine', '').replace('restaurant', '').replace(' ', '').strip()
    if cuisine == "indian":
        return "indpak"
    elif cuisine == "american":
        return "newamerican"
    return cuisine


def proc_phone_str(phone: str) -> str:
    return phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '').strip()


# Time string formats (excl. date)
t_formats = ("%I:%M%p", "%I%p", "%H:%M", "%H")

# Number conversion
units = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
)
tens = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
scales = ("hundred", "thousand", "million", "billion", "trillion")

# Cuisine choices
cuisines = {
    "chinese", "american", "japanese", "korean", "indian", "italian", "french", "mexican", "portuguese", "turkish"
}


def text2int(text_num: str) -> int:
    tmp = {"and": (1, 0)}
    for idx, word in enumerate(units):
        tmp[word] = (1, idx)
    for idx, word in enumerate(tens):
        tmp[word] = (1, idx * 10)
    for idx, word in enumerate(scales):
        tmp[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in text_num.lower().split():
        if word not in tmp:
            return -1

        scale, increment = tmp[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def parse_int(n: str) -> int:
    try:
        return int(n)
    except ValueError:
        # Returns -1 if n is invalid
        return text2int(n)


def validate_phone_number(phone):
    phone = proc_phone_str(phone)
    return len(phone) == 10 and phone.isdigit()


def validate_date(date):
    date = _RE_WHITESPACE.sub(" ", date).strip().lower()
    if 'yesterday' in date or 'before today' in date or 'prior to today' in date:
        return False
    if 'tomorrow' in date or 'after today' in date or date == 'today':
        return True
    today = datetime.today()
    try:
        date = parser.parse(date)
    except ValueError:
        return False
    # If the original date doesn't have a year, AWS will append the next year to it. Thus, we can't return date >= today
    return (date.year == today.year and date.month >= today.month and date.day >= today.day) or \
           (date.year - today.year == 1 and (date - today).days < 90)


def validate_time(timestr, is_today):
    timestr = timestr.replace(' ', '').lower().replace('a.m.', 'am').replace('p.m.', 'pm').replace('.', ':')
    for t_format in t_formats:
        try:
            if is_today:
                return datetime.strptime(timestr, t_format).time() > datetime.now().time()
            else:
                return True
        except ValueError:
            pass
    else:
        return False


def validate_email(email):
    if "@" not in email:
        return False
    return True


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_details(location, cuisine, dining_date, dining_time, n_people, phone_number, email):
    # Delegate the validations of other information to Lex, as the formats can be very flexible.
    if cuisine is not None:
        cuisine = cuisine.lower().replace('cuisine', '').replace('restaurant', '').replace(' ', '')
        if cuisine not in cuisines:
            return build_validation_result(
                False,
                'Cuisine',
                'Sorry, the cuisine {} you sent was unavailable. Cuisines: {}.'.format(
                    cuisine,
                    ', '.join([c.capitalize() for c in cuisines]))
            )

    if dining_date is not None:
        if not validate_date(dining_date):
            return build_validation_result(
                False,
                'DiningDate',
                'Sorry, I don\'t understand the date format, or the date you sent was in the past. '
                'Please give me a date no earlier than today {}.'.format(datetime.now().strftime("%m/%d/%Y"))
            )

        is_today = parser.parse(dining_date).date() == datetime.today().date()
        if dining_time is not None and not validate_time(dining_time, is_today):
            return build_validation_result(
                False,
                'DiningTime',
                'Sorry, the time you sent was either in an invalid format or in the past. '
                'Please give me a valid time.'
            )

    if n_people is not None:
        n_people = parse_int(n_people)
        if n_people < 1:
            return build_validation_result(
                False,
                'NumberOfPeople',
                'Sorry, the number of people {} you sent was invalid. Please send me a number >= 1.'.format(n_people)
            )

    if phone_number is not None and not validate_phone_number(phone_number):
        return build_validation_result(
            False,
            'PhoneNumber',
            'Sorry, the phone number you sent was invalid. A valid phone number should contain only 10 digits.'
        )

    if email is not None and not validate_email(email):
        return build_validation_result(
            False,
            'Email',
            'Sorry, the email you sent was invalid. Please send a correct one!'
        )

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def proc_dining_details(intent_request, sess_attr):
    """
    Performs dialog management and fulfillment for dining suggestions.
    """
    slots = get_slots(intent_request)
    location = slots['Location']
    cuisine = slots['Cuisine']
    dining_date = slots['DiningDate']
    dining_time = slots['DiningTime']
    n_people = slots['NumberOfPeople']
    phone = slots['PhoneNumber']
    email = slots['Email']

    # email = sess_attr["Email"]

    source = intent_request['invocationSource']
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        validation_result = validate_details(location, cuisine, dining_date, dining_time, n_people, phone, email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(sess_attr,
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        return delegate(sess_attr, get_slots(intent_request))

    # Send collected info to SQS and return a closing message
    sqs_message_attr = {
        'phone': {
            'DataType': 'String',
            'StringValue': proc_phone_str(phone)
        },
        'email': {
            'DataType': 'String',
            'StringValue': email
        },
        'location': {
            'DataType': 'String',
            'StringValue': location
        },
        'cuisine': {
            'DataType': 'String',
            'StringValue': proc_cuisine_str(cuisine)
        },
        'date': {
            'DataType': 'String',
            'StringValue': dining_date
        },
        'time': {
            'DataType': 'String',
            'StringValue': dining_time
        },
        'people': {
            'DataType': 'Number',
            'StringValue': n_people
        },
        'userId': {
            'DataType': 'String',
            'StringValue': intent_request['userId']
        }
    }
    sqs_response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=8,
        MessageAttributes=sqs_message_attr,
        MessageBody='Dining information for userId {}.'.format(intent_request['userId'])
    )
    return close(
        sess_attr,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thank you. You\'re all set! Ticket ID: {}. '
                       'Suggestions will be sent to email {} shortly.'.format(
                sqs_response['MessageId'], email)
        }
    )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    # logger.debug('dispatch userId={}, intentName={}'.format(
    #     intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']
    # print("sessionAttributes: ", intent_request["sessionAttributes"])
    sess_attr = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return proc_dining_details(intent_request, sess_attr)
    # elif intent_name == 'GreetingIntent':
    #     return delegate(sess_attr, slots={})
    # elif intent_name == 'ThankYouIntent':
    #     return delegate(sess_attr, slots={})
    else:
        # Use the settings in console
        return delegate(sess_attr, slots={})


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    # logger.debug('event.bot.name={}'.format(event['bot']['name']))
    logger.debug(event)
    return dispatch(event)
