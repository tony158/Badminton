import base64
import os

import boto3
from urllib import request, parse
from twilio.rest import Client

SNS_TOPIC_ARN = 'arn:aws:sns:eu-west-1:715834233805:badminton_sns_topic'

TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
# TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

TWILIO_ACCOUNT_SID = 'AC4509d80d62e9d9bbb544bb1adacd0865'
TWILIO_AUTH_TOKEN = 'b57737ba9d3c13ab12c4dba0489e8d1c'


def send_sms_twilio(content: dict):
    to_number = '+353871136737'
    from_number = '+13854104751'
    body = format_2_sms(content)

    if not TWILIO_ACCOUNT_SID:
        return "Unable to access Twilio Account SID."
    elif not TWILIO_AUTH_TOKEN:
        return "Unable to access Twilio Auth Token."
    elif not to_number:
        return "The function needs a 'To' number in the format +12023351493"
    elif not from_number:
        return "The function needs a 'From' number in the format +19732644156"
    elif not body:
        return "The function needs a 'Body' message to send."

    # insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)
    post_params = {"To": to_number, "From": from_number, "Body": body}

    # encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # add authentication header to request based on Account SID + Auth Token
    authentication = "{}:{}".format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

    try:
        with request.urlopen(req, data) as f:
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        print('Twilio something went wrong!')
        print(e)
        return e

    return "SMS sent successfully!"


def twilio_test(content: dict):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        messaging_service_sid='MG082d0efa245999d499215633bc271d2c',
        body='aaaa',
        to='+353871136737'
    )


def send_sms_pinpoint(content: dict):
    if not bool(content):
        return

    sms_content = format_2_sms(content)

    pinpoint = boto3.client('pinpoint')
    response = pinpoint.send_messages(
        ApplicationId='6064579a63104f83911d6aa9cfe3de81',  # Project ID in Pinpoint console
        MessageRequest={
            'Addresses': {
                '+353871136737': {'ChannelType': 'SMS'}
            },
            'MessageConfiguration': {
                'SMSMessage': {
                    'Body': sms_content,
                    'MessageType': 'PROMOTIONAL'
                }
            }
        }
    )
    return response


def send_sms_sns(content: dict):
    sns = boto3.client('sns')
    sms_content = format_2_sms(content)
    sns.publish(Message=sms_content, TopicArn=SNS_TOPIC_ARN)


def format_2_sms(content: str):
    sms = 'Badminton court available:\n-----\n'
    for available_hour in content:
        sms += available_hour['date'] + '\n' + str(available_hour['available_hours']) + '\n'
        sms += '-----\n'
    return sms
