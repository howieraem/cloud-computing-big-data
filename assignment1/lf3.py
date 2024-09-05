import json
import boto3

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


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


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
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


def validate_email(email):
    if "@" not in email:
        return False
    return True


def validate_details(email):
    if email is not None and not validate_email(email):
        return build_validation_result(
            False,
            'Email',
            'Sorry, the email you sent was invalid. Please send a correct one!'
        )

    return build_validation_result(True, None, None)


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


def query_business_data(email, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table = dynamodb.Table("HistorySugg")

    response = table.query(KeyConditionExpression=Key("email").eq(email))
    history = ""
    for item in response["Items"]:
        if not isinstance(item, dict):
            continue
        history = item["message"] if "message" in item else ""
        if history:
            break

    return history


def proc_dining_details(intent_request, sess_attr):
    slots = get_slots(intent_request)

    email = slots["Email"]
    if "Email" not in sess_attr or not sess_attr["Email"]:
        sess_attr['Email'] = email

    source = intent_request['invocationSource']
    if source == 'DialogCodeHook':
        # print(email)
        validation_result = validate_details(email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(sess_attr,
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
        # print('GOT HERE')
        return delegate(sess_attr, get_slots(intent_request))

    history_message = query_business_data(email)
    if history_message:
        print("SESS_ATTR", sess_attr)
        return close(
            sess_attr,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Thank you. Our previous suggestion is %s. If you want other suggestion, please type continue!' % history_message
            }
        )
    else:
        print("SESS_ATTR", sess_attr)
        return close(
            sess_attr,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Thank you. Let me ask you a few more questions about your dining preferences.'
            }
        )


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    # logger.debug('dispatch userId={}, intentName={}'.format(
    #     intent_request['userId'], intent_request['currentIntent']['name']))
    # print("REQ:", intent_request, intent_request['currentIntent']['name'])
    intent_name = intent_request['currentIntent']['name']
    sess_attr = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # Dispatch to your bot's intent handlers
    if intent_name == 'GetCacheIntent':
        return proc_dining_details(intent_request, sess_attr)
    else:
        # Use the settings in console
        return delegate(sess_attr, slots={})


def lambda_handler(event, context):
    # TODO implement
    print("event:", event)
    return dispatch(event)
