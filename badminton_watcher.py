# Badminton watcher
import json
import re
import urllib
from urllib.request import Request, urlopen
import datetime

from telegram_sender import send_to_telegram

LAMBDA_EXECUTION_HOUR = [8, 24]

BADMINTON_URL = 'https://terenurebadminton.mycourts.co.uk/'
# st1: startTime, st2: endTime, d: days from today, tabID: 161(court 1-4), 162(court 5-6)
BOOKING_URL = BADMINTON_URL + 'bookings.asp?st1={0}&st2={1}&d={2}&tabID={3}'
REQUEST_PARAMS = [600, 2400, 162]  # [startTime, endTime, tabID]

DAYS_TO_CHECK_FROM_TODAY = 7


def lambda_handler(event, context):
    # if not should_run_now():
    #     return {'sleepingTime': 'True'}

    if not website_is_up():
        return {'statusOfWebsite': 'Down'}

    desired_date_time = data = json.load(open('desired_datetime.json'))
    desired_request = generate_desired_day_hours_urls(desired_date_time)

    all_availabilities = []
    for request in desired_request:
        desired_hours = request['desired_hours']
        available_hours = make_request(request)

        temp_result = set(desired_hours) & set(available_hours)
        if temp_result:
            all_availabilities.append({
                'date': request['the_date'] + " " + request['weekday'],
                'available_hours': sorted(temp_result)})

    print(json.dumps(all_availabilities, indent=4))

    if bool(all_availabilities):
        send_to_telegram(all_availabilities)

    return all_availabilities


def make_request(desired: {}):
    request = Request(desired['url'])
    response = urlopen(request).read().decode()

    available_booking_hours = extract_available_booking_hours(str(response))
    return available_booking_hours


def generate_desired_day_hours_urls(desired_date_time):
    date_time_dict = {}
    for date_hours in desired_date_time:
        desired_weekday = date_hours['weekday']
        desired_hours = date_hours['desired_hours']
        date_time_dict[desired_weekday] = desired_hours

    result_list = []
    for d in range(DAYS_TO_CHECK_FROM_TODAY):
        the_date_to_check = (datetime.datetime.now() + datetime.timedelta(days=d))
        desired_weekday = the_date_to_check.strftime("%A")

        desired_hours = date_time_dict.get(desired_weekday)
        url = BOOKING_URL.format(REQUEST_PARAMS[0], REQUEST_PARAMS[1], d, REQUEST_PARAMS[2])

        if (desired_hours is not None) and (desired_weekday is not None):
            result_list.append({'weekday': desired_weekday,
                                'the_date': the_date_to_check.strftime("%Y-%m-%d"),
                                'd': d,
                                'desired_hours': desired_hours,
                                'url': url})

    return result_list


# <span class="starttime">1000: </span>
def extract_available_booking_hours(response: str):
    response_len = len(response)
    booking_start_tag = '<span class="starttime">'
    booking_end_tag = '</span>'
    book_now_tag = '<span class="booknow">book now</span>'

    count = response.count(book_now_tag)

    result = []
    search_start_pos = 0

    while count > 0:
        book_now_index = response.index(book_now_tag, search_start_pos)
        start_index = max(book_now_index - len(booking_start_tag) - len(booking_end_tag) - 10, 0)

        available_hour_substring = response[start_index:book_now_index]
        available_hour = re.search(booking_start_tag + '(.*)' + booking_end_tag, available_hour_substring).group(1)
        result.append(available_hour.replace(':', '').strip())

        search_start_pos = min(book_now_index + len(book_now_tag), response_len)
        count -= 1

    return result


def website_is_up():
    status_code = urllib.request.urlopen(BADMINTON_URL).getcode()
    return status_code == 200


def should_run_now():
    return LAMBDA_EXECUTION_HOUR[0] < datetime.datetime.now().hour < LAMBDA_EXECUTION_HOUR[1]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    lambda_handler({}, {})
