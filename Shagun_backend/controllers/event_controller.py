import io
import json
import os
import time
from datetime import datetime

import firebase_admin
import pymysql
import qrcode
from PIL import Image, ImageOps
from django.conf import settings
from django.db import connection
from firebase_admin import credentials, messaging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from Shagun_backend.controllers.credentials import get_credentials
from Shagun_backend.util import responsegenerator
from Shagun_backend.util.constants import *
from Shagun_backend.util.responsegenerator import responseGenerator

firebase_cred_path = "firebase_cred/shagun-20c2a-firebase-adminsdk-bef1u-ab9b696d2d.json"
full_firebase_cred_path = os.path.join(settings.MEDIA_ROOT, firebase_cred_path)
cred = credentials.Certificate(full_firebase_cred_path)
firebase_admin.initialize_app(cred)


def send_push_notification(device_token, title, message):
    try:
        notification = messaging.Notification(title=title, body=message)
        message = messaging.Message(notification=notification, token=device_token)
        messaging.send(message)
    except Exception as e:
        print(f"Error sending FCM notification: {str(e)}")


def create_event(event_obj):
    try:
        with connection.cursor() as cursor:
            sub_events_json = json.dumps([sub_event.__dict__ for sub_event in event_obj.sub_events])
            event_admin_json = json.dumps([event_admins.__dict__ for event_admins in event_obj.event_admin])

            create_event_query = """INSERT INTO event (created_by_uid, event_type_id, city_id, address_line1,
                                        address_line2, event_lat_lng, created_on, sub_events, event_date, event_note, 
                                        event_admin, is_approved, status, printer_id, delivery_fee, delivery_address, 
                                        updated_by, updated_on) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            values = (event_obj.created_by_uid, event_obj.event_type_id, event_obj.city_id, event_obj.address_line1,
                      event_obj.address_line2, event_obj.event_lat_lng, getIndianTime(), sub_events_json,
                      event_obj.event_date, event_obj.event_note, event_admin_json, False, True, event_obj.printer_id,
                      event_obj.delivery_fee, event_obj.delivery_address, event_obj.updated_by, getIndianTime())

            cursor.execute(create_event_query, values)
            event_id = cursor.lastrowid
            event_admin_query = f"""SELECT e.event_admin, et.event_type_name FROM event AS e
                                    LEFT JOIN events_type AS et ON e.event_type_id = et.id
                                    WHERE  e.id = '{event_id}'"""
            cursor.execute(event_admin_query)
            admin = cursor.fetchone()
            event_admins = json.loads(admin[0])

            for item in event_admins:
                uid = item["uid"]
                event_created_notification_query = f"""INSERT INTO notification (uid, type, title, message, created_on) 
                            VALUES ('{uid}', 'event',
                            'Event has been created',
                            ' Event created for {admin[1]} on {event_obj.event_date}',
                            '{getIndianTime()}')"""
                cursor.execute(event_created_notification_query)

                phone_query = f"""SELECT phone, fcm_token FROM users WHERE  uid = '{uid}'"""
                cursor.execute(phone_query)
                user_data = cursor.fetchone()
                title = f"Event has been created"
                message = f"Event created for {admin[1]} on {event_obj.event_date}"
                send_push_notification(user_data[1], title, message)
                deep_link = get_credentials()
                text = deep_link.get("deep_link") + "eventId=" + str(event_id) + "&invitedBy=" + user_data[0]

                logo_path = "static/images/square_logo.jpg"
                logo = Image.open(logo_path)

                basewidth = 100

                # adjust image size
                wpercent = (basewidth / float(logo.size[0]))
                hsize = int((float(logo.size[1]) * float(wpercent)))

                logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
                QRcode = qrcode.QRCode(
                    error_correction=qrcode.constants.ERROR_CORRECT_H
                )

                QRcode.add_data(text)

                QRcode.make()
                QRcolor = '#671160'

                QRimg = QRcode.make_image(
                    fill_color=QRcolor, back_color="white").convert('RGB')

                pos = ((QRimg.size[0] - logo.size[0]) // 2,
                       (QRimg.size[1] - logo.size[1]) // 2)
                QRimg.paste(logo, pos)

                media_dir = os.path.join(settings.MEDIA_ROOT, 'images', 'qr_codes')
                os.makedirs(media_dir, exist_ok=True)
                image_path = os.path.join(media_dir, f"""{event_id}_{user_data[0]}.png""")

                QRimg.save(image_path)

                image_url = f"""images/qr_codes/{event_id}_{user_data[0]}.png"""
                item["qr_code"] = image_url

                date_obj = datetime.datetime.strptime(event_obj.event_date, "%Y-%m-%d %H:%M:%S")
                month = date_obj.strftime("%b")
                day = date_obj.strftime("%a")
                date = date_obj.strftime("%d")
                hour = date_obj.strftime("%I:%M %p")

                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                try:
                    driver.get('http://127.0.0.1:8000/view_qr?'
                               'qr_owner=' + str(item['name']) +
                               '&qr_image=' + str(item["qr_code"]) +
                               '&admins=' + str(event_admins) +
                               '&date=' + date +
                               '&month=' + month +
                               '&day=' + day +
                               '&time=' + hour +
                               '&event_type=' + admin[1])
                    total_height = driver.execute_script("return document.body.scrollHeight")
                    driver.set_window_size(500, total_height)
                    scroll_offset = 0
                    screenshot_parts = []
                    while scroll_offset < total_height:
                        screenshot = driver.get_screenshot_as_png()
                        img = Image.open(io.BytesIO(screenshot))
                        img = ImageOps.exif_transpose(img)
                        img.save(os.path.join(settings.MEDIA_ROOT, image_url), format='PNG', quality=100, optimize=True)
                        screenshot_parts.append(screenshot)
                        scroll_offset += 600
                        driver.execute_script(f"window.scrollTo(0, {scroll_offset});")
                        time.sleep(2)
                    full_screenshot = Image.new('RGB', (500, total_height))
                    y_offset = 0
                    for screenshot_part in screenshot_parts:
                        img = Image.open(io.BytesIO(screenshot_part))
                        full_screenshot.paste(img, (0, y_offset))
                        y_offset += img.height
                    full_screenshot.save(os.path.join(settings.MEDIA_ROOT, image_url), format='PNG', quality=100,
                                         optimize=True)
                finally:
                    driver.quit()

            update_qr_sql = f"""UPDATE event SET event_admin = '{json.dumps(event_admins)}' WHERE id = '{event_id}' """
            cursor.execute(update_qr_sql)
            return {
                "status": True,
                "message": "Event Created successfully"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def edit_event(event_obj, event_id):
    try:
        with connection.cursor() as cursor:
            sub_events_json = json.dumps([sub_event.__dict__ for sub_event in event_obj.sub_events])
            update_event_query = """
                        UPDATE event
                        SET
                            event_type_id = %s,
                            city_id = %s,
                            printer_id = %s,
                            address_line1 = %s,
                            address_line2 = %s,
                            event_lat_lng = %s,
                            sub_events = %s,
                            event_date = %s,
                            event_note = %s,
                            delivery_fee = %s,
                            delivery_address = %s,
                            updated_by = %s,
                            updated_on = %s
                        WHERE
                            id = %s
                    """

            values = (
                event_obj.event_type_id, event_obj.city_id, event_obj.printer_id,
                event_obj.address_line1, event_obj.address_line2, event_obj.event_lat_lng,
                sub_events_json, event_obj.event_date, event_obj.event_note, event_obj.delivery_fee,
                event_obj.delivery_address, event_obj.updated_by, getIndianTime(), event_id)
            cursor.execute(update_event_query, values)

            event_admin_query = f"""SELECT e.event_admin, et.event_type_name FROM event AS e
                                                LEFT JOIN events_type AS et ON e.event_type_id = et.id
                                                WHERE  e.id = '{event_id}'"""
            cursor.execute(event_admin_query)
            admin = cursor.fetchone()
            event_admins = json.loads(admin[0])
            for item in event_admins:
                uid = item["uid"]
                event_created_notification_query = f"""INSERT INTO notification (uid, type, title, message, created_on) 
                                            VALUES ('{uid}', 'event',
                                            'Event has been created',
                                            ' Event created for {admin[1]} on {event_obj.event_date}',
                                            '{getIndianTime()}')"""
                cursor.execute(event_created_notification_query)

                phone_query = f"""SELECT phone, fcm_token FROM users WHERE  uid = '{uid}'"""
                cursor.execute(phone_query)
                user_data = cursor.fetchone()
                title = f"Event has been created"
                message = f"Event created for {admin[1]} on {event_obj.event_date}"
                send_push_notification(user_data[1], title, message)
                deep_link = get_credentials()
                text = deep_link.get("deep_link") + "eventId=" + str(event_id) + "&invitedBy=" + user_data[0]

                logo_path = "static/images/square_logo.jpg"
                logo = Image.open(logo_path)

                basewidth = 100

                # adjust image size
                wpercent = (basewidth / float(logo.size[0]))
                hsize = int((float(logo.size[1]) * float(wpercent)))

                logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
                QRcode = qrcode.QRCode(
                    error_correction=qrcode.constants.ERROR_CORRECT_H
                )

                QRcode.add_data(text)

                QRcode.make()
                QRcolor = '#671160'

                QRimg = QRcode.make_image(
                    fill_color=QRcolor, back_color="white").convert('RGB')

                pos = ((QRimg.size[0] - logo.size[0]) // 2,
                       (QRimg.size[1] - logo.size[1]) // 2)
                QRimg.paste(logo, pos)

                media_dir = os.path.join(settings.MEDIA_ROOT, 'images', 'qr_codes')
                os.makedirs(media_dir, exist_ok=True)
                image_path = os.path.join(media_dir, f"""{event_id}_{user_data[0]}.png""")

                QRimg.save(image_path)

                image_url = f"""images/qr_codes/{event_id}_{user_data[0]}.png"""
                item["qr_code"] = image_url

                date_obj = datetime.datetime.strptime(event_obj.event_date, "%Y-%m-%d %H:%M:%S")
                month = date_obj.strftime("%b")
                day = date_obj.strftime("%a")
                date = date_obj.strftime("%d")
                hour = date_obj.strftime("%I:%M %p")

                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                try:
                    driver.get('http://127.0.0.1:8000/view_qr?'
                               'qr_owner=' + str(item['name']) +
                               '&qr_image=' + str(item["qr_code"]) +
                               '&admins=' + str(event_admins) +
                               '&date=' + date +
                               '&month=' + month +
                               '&day=' + day +
                               '&time=' + hour +
                               '&event_type=' + admin[1])
                    total_height = driver.execute_script("return document.body.scrollHeight")
                    driver.set_window_size(500, total_height)
                    scroll_offset = 0
                    screenshot_parts = []
                    while scroll_offset < total_height:
                        screenshot = driver.get_screenshot_as_png()
                        img = Image.open(io.BytesIO(screenshot))
                        img = ImageOps.exif_transpose(img)
                        img.save(os.path.join(settings.MEDIA_ROOT, image_url), format='PNG', quality=100, optimize=True)
                        screenshot_parts.append(screenshot)
                        scroll_offset += 600
                        driver.execute_script(f"window.scrollTo(0, {scroll_offset});")
                        time.sleep(2)
                    full_screenshot = Image.new('RGB', (500, total_height))
                    y_offset = 0
                    for screenshot_part in screenshot_parts:
                        img = Image.open(io.BytesIO(screenshot_part))
                        full_screenshot.paste(img, (0, y_offset))
                        y_offset += img.height
                    full_screenshot.save(os.path.join(settings.MEDIA_ROOT, image_url), format='PNG', quality=100,
                                         optimize=True)
                finally:
                    driver.quit()

                event_created_notification_query = f"""INSERT INTO notification (uid, type, title, message, created_on) 
                                        VALUES ('{uid}', 'event',
                                        'Event has been updated',
                                        ' Event updated for {admin[1]} on {event_obj.event_date}',
                                        '{getIndianTime()}')"""
                cursor.execute(event_created_notification_query)

                phone_query = f"""SELECT phone, fcm_token FROM users WHERE  uid = '{uid}'"""
                cursor.execute(phone_query)
                user_data = cursor.fetchone()

                title = f"Event has been Updated"
                message = f"Event created for {admin[1]} on {event_obj.event_date}"
                send_push_notification(user_data[1], title, message)

            update_qr_sql = f"""UPDATE event SET event_admin = '{json.dumps(event_admins)}' WHERE id = '{event_id}' """
            cursor.execute(update_qr_sql)

            return {
                "status": True,
                "message": "Event Updated successfully"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def enable_disable_event(e_id, et_status, updated_by):
    try:
        with connection.cursor() as cursor:
            disable_event_query = "UPDATE event SET status = %s,updated_by = %s WHERE id = %s"
            values = (et_status, updated_by, e_id)
            cursor.execute(disable_event_query, values)
            return {
                "status": True,
                "message": "Event Status changed successfully"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301

    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_event_by_id(et_id):
    try:
        with connection.cursor() as cursor:
            get_event_query = f""" SELECT e.*, et.event_type_name,
            l.city_name, p.store_name, creator.name, updator.name FROM event e
            LEFT JOIN users AS creator ON e.created_by_uid = creator.uid
            LEFT JOIN users AS updator ON e.updated_by = updator.uid
            LEFT JOIN events_type et ON e.event_type_id = et.id
            LEFT JOIN locations l ON e.city_id = l.id
            LEFT JOIN printer p ON e.printer_id = p.id
            WHERE e.id = '{et_id}'"""
            cursor.execute(get_event_query)
            event_data = cursor.fetchone()
            if event_data is not None:
                return {
                    "status": True,
                    "event_data": responsegenerator.responseGenerator.generateResponse(event_data, EVENT_BY_ID)
                }, 200
            else:
                return {
                    "status": False,
                    "event": None
                }, 301

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def event_settlement(status):
    try:
        with connection.cursor() as cursor:
            event_settlement_query = f"""
                    SELECT e.* ,
                      IFNULL(SUM(th.shagun_amount), 0) AS total_received_amount,
                      IFNULL(SUM(CASE WHEN th.is_settled = 0 THEN th.shagun_amount ELSE 0 END), 0) AS pending_shagun_amount,
                      IFNULL(SUM(CASE WHEN th.is_settled = 1 THEN th.shagun_amount ELSE 0 END), 0) AS settled_amount,
                      et.event_type_name
                    FROM event e
                    LEFT JOIN transaction_history th ON e.id = th.event_id
                    LEFT JOIN events_type et ON e.event_type_id = et.id
                    WHERE e.status = '{status}'
                    GROUP BY e.id, e.event_date ORDER BY e.id DESC ;
                    """
            cursor.execute(event_settlement_query)
            amount = cursor.fetchall()
            return {
                "status": True,
                # "msg": amount
                "event_settlement": responsegenerator.responseGenerator.generateResponse(amount, ACTIVE_EVENT)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def search_event_settlement(search):
    try:
        with connection.cursor() as cursor:
            event_settlement_query = f"""
                    SELECT e.* ,
                      IFNULL(SUM(th.shagun_amount), 0) AS total_received_amount,
                      IFNULL(SUM(CASE WHEN th.is_settled = 0 THEN th.shagun_amount ELSE 0 END), 0) 
                      AS pending_shagun_amount,
                      IFNULL(SUM(CASE WHEN th.is_settled = 1 THEN th.shagun_amount ELSE 0 END), 0) AS settled_amount,
                      et.event_type_name
                    FROM event e
                    LEFT JOIN transaction_history th ON e.id = th.event_id
                    LEFT JOIN events_type et ON e.event_type_id = et.id
                    WHERE e.id = '{search}'  OR  et.event_type_name LIKE '%{search}%' 
                    OR LOWER(e.event_admin) LIKE LOWER ('%%{search}%%')
                    GROUP BY e.id ORDER BY e.created_on DESC;
                    """

            cursor.execute(event_settlement_query)
            amount = cursor.fetchall()
            return {
                "status": True,
                "event_settlement": responsegenerator.responseGenerator.generateResponse(amount, ACTIVE_EVENT)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_event_by_approval_status(status):
    try:
        with connection.cursor() as cursor:
            event_list_query = f"""SELECT e.event_date, e.event_admin, et.event_type_name, e.id, 
                                              e.is_approved, e.status, creator.name, updator.name, e.created_on, e.updated_on  
                                              FROM event AS e
                                                LEFT JOIN users AS creator ON e.created_by_uid = creator.uid
                                                LEFT JOIN users AS updator ON e.updated_by = updator.uid
                                                LEFT JOIN events_type AS et ON e.event_type_id = et.id 
                                              WHERE e.is_approved LIKE '{status}' ORDER BY e.id DESC """
            cursor.execute(event_list_query)
            events = cursor.fetchall()
            return {
                "status": True,
                "event_list": responsegenerator.responseGenerator.generateResponse(events, ALL_EVENT_LIST)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def gift_event(e_id, phone):
    try:
        with connection.cursor() as cursor:
            gift_event_query = f""" SELECT * , (SELECT uid FROM users WHERE phone = '{phone}') AS users FROM event 
            WHERE id = '{e_id}'"""
            cursor.execute(gift_event_query)
            event = cursor.fetchone()
            if event is not None:
                return {
                    "status": True,
                    "gift_event": responsegenerator.responseGenerator.generateResponse(event, GIFT_EVENT)
                }, 200
            else:
                return {
                    "status": False,
                    "event": None
                }, 301

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_event_list(uid):
    try:
        with connection.cursor() as cursor:
            event_list_query = """SELECT event.event_date, event.event_admin, events_type.event_type_name, event.id, 
                                  event.is_approved, event.status FROM event LEFT JOIN events_type ON
                                  event.event_type_id = events_type.id ORDER BY event.created_on DESC"""
            cursor.execute(event_list_query)
            events = cursor.fetchall()
            return {
                "status": True,
                "event_list": responsegenerator.responseGenerator.generateResponse(events, EVENT_LIST)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_single_event(event_id, phone):
    try:
        with connection.cursor() as cursor:
            single_event_query = f"""SELECT 
                                        event.event_date, event.event_admin, event.event_note, 
                                        event.address_line1, event.address_line2, event.event_lat_lng, 
                                        event.sub_events, events_type.event_type_name, users.uid, users.name , event.id, 
                                        event.delivery_fee
                                    FROM event
                                    LEFT JOIN events_type ON event.event_type_id = events_type.id
                                    LEFT JOIN users ON users.phone = '{phone}'
                                    WHERE event.id = '{event_id}'"""
            cursor.execute(single_event_query)
            events = cursor.fetchone()
            return {
                "status": True,
                "event": responsegenerator.responseGenerator.generateResponse(events, SINGLE_EVENT)
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def create_events_type(event_name, created_by, updated_by):
    try:
        with connection.cursor() as cursor:
            events_type_query = """INSERT INTO events_type (event_type_name, status, created_by, created_on, updated_by, 
                                    updated_on) VALUES (%s,%s,%s,%s,%s,%s)"""
            values = (event_name, True, created_by, getIndianTime(), updated_by, getIndianTime())
            cursor.execute(events_type_query, values)
            return {
                "status": True,
                "message": "Event Type added successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def disable_events_type(event_id, e_status):
    try:
        with connection.cursor() as cursor:
            disable_events_type_query = "UPDATE events_type SET status = %s WHERE id = %s"
            values = (e_status, event_id)
            cursor.execute(disable_events_type_query, values)
            return {
                "status": True,
                "message": "Event Type changed successfully"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301

    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def edit_events_type(lid, event_type_name, updated_by):
    try:
        with connection.cursor() as cursor:
            edit_query = f"""UPDATE events_type SET event_type_name = '{event_type_name}' , updated_by = '{updated_by}', 
                            updated_on = %s where id= '{lid}'"""
            cursor.execute(edit_query, (getIndianTime(),))
            return {
                "status": True,
                "message": "Events Type edited successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def events_type_by_id(et_id):
    try:
        with connection.cursor() as cursor:
            events_type_query = " SELECT id, event_type_name FROM events_type WHERE id= %s;"
            cursor.execute(events_type_query, [et_id, ])
            events = cursor.fetchone()
            if events is not None:
                return {
                    "status": True,
                    "event_type": responsegenerator.responseGenerator.generateResponse(events, EVENT_TYPE_BY_ID)
                }, 200
            else:
                return {
                    "status": False,
                    "event_type": None
                }, 301

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_event_type_list_for_user():
    try:
        with connection.cursor() as cursor:
            event_type_list_query = """SELECT * FROM events_type WHERE status=1"""
            cursor.execute(event_type_list_query)
            event_type_list = cursor.fetchall()

            return {
                "status": True,
                "event_type_list": responseGenerator.generateResponse(event_type_list, EVENT_TYPE_LIST)

            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def add_location(city_name, created_by, updated_by):
    try:
        with connection.cursor() as cursor:
            add_location_query = """INSERT INTO locations (city_name, status, created_by, created_on, updated_by, 
                                    updated_on) 
                                    VALUES (%s, %s, %s,%s ,%s , %s)"""
            values = (city_name, True, created_by, getIndianTime(), updated_by, getIndianTime())
            cursor.execute(add_location_query, values)
            return {
                "status": True,
                "message": "location added successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def disable_location(location_id, loc_status):
    try:
        with connection.cursor() as cursor:
            disable_loc_query = "UPDATE locations SET status = %s WHERE id = %s"
            values = (loc_status, location_id)
            cursor.execute(disable_loc_query, values)
            return {
                "status": True,
                "message": "Location status changed successfully"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301

    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def edit_location(lid, city_name, updated_by):
    try:
        with connection.cursor() as cursor:
            edit_location_query = f"""UPDATE locations SET city_name = '{city_name}' , updated_by = '{updated_by}',
                                        updated_on = '{getIndianTime()}' where id= '{lid}' """
            cursor.execute(edit_location_query)
            return {
                "status": True,
                "message": "Location edited successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_location_by_id(loc_id):
    try:
        with connection.cursor() as cursor:
            get_location_query = " SELECT id, city_name FROM locations WHERE id=%s;"
            cursor.execute(get_location_query, [loc_id])
            location = cursor.fetchone()
            if location is not None:
                return {
                    "status": True,
                    "location": responsegenerator.responseGenerator.generateResponse(location, EVENT_TYPE_BY_ID)
                }, 200
            else:
                return {
                    "status": False,
                    "location": None
                }, 301

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_event_type_list_for_admin():
    try:
        with connection.cursor() as cursor:
            event_type_for_admin_query = """SELECT e.id, e.event_type_name, e.status, creator.name, updator.name, 
                                            e.created_on, e.updated_on 
                                            FROM events_type AS e
                                            LEFT JOIN users AS creator ON e.created_by = creator.uid
                                            LEFT JOIN users AS updator ON e.updated_by = updator.uid"""
            cursor.execute(event_type_for_admin_query)
            events = cursor.fetchall()
            return {
                "status": True,
                "events_type": responsegenerator.responseGenerator.generateResponse(events, ALL_EVENT_TYPE_LIST)
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def filter_event_type_list_for_admin(status):
    try:
        with connection.cursor() as cursor:
            event_type_for_admin_query = f"""SELECT e.id, e.event_type_name, e.status, creator.name, updator.name, 
                                            e.created_on, e.updated_on 
                                            FROM events_type AS e
                                            LEFT JOIN users AS creator ON e.created_by = creator.uid
                                            LEFT JOIN users AS updator ON e.updated_by = updator.uid
                                            WHERE e.status= '{status}'"""
            cursor.execute(event_type_for_admin_query)
            events = cursor.fetchall()
            return {
                "status": True,
                "events_type": responsegenerator.responseGenerator.generateResponse(events, ALL_EVENT_TYPE_LIST)
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_locations_list():
    try:
        with connection.cursor() as cursor:
            location_list_query = """SELECT l.id, l.city_name, l.status, creator.name, updator.name, l.created_on, 
                                        l.updated_on FROM locations AS l
                                        LEFT JOIN users AS creator ON l.created_by = creator.uid
                                        LEFT JOIN users AS updator ON l.updated_by = updator.uid"""
            cursor.execute(location_list_query)
            events = cursor.fetchall()
            return {
                "status": True,
                "locations": responsegenerator.responseGenerator.generateResponse(events, ALL_LOCATION_LIST)
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def filter_locations_list(status):
    try:
        with connection.cursor() as cursor:
            location_list_query = f"""SELECT l.id, l.city_name, l.status, creator.name, updator.name, l.created_on, 
                                        l.updated_on FROM locations AS l
                                        LEFT JOIN users AS creator ON l.created_by = creator.uid
                                        LEFT JOIN users AS updator ON l.updated_by = updator.uid
                                        WHERE l.status = '{status}'"""
            cursor.execute(location_list_query)
            events = cursor.fetchall()
            return {
                "status": True,
                "locations": responsegenerator.responseGenerator.generateResponse(events, ALL_LOCATION_LIST)
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_my_event_list(uid):
    try:
        with connection.cursor() as cursor:
            phone_query = f"""SELECT phone FROM users WHERE uid = '{uid}'"""
            cursor.execute(phone_query)
            phone = cursor.fetchone()[0]
            # SQL query for events with event_date less than or equal to today
            sql_query_my_events = f"""
                    SELECT event.event_date, event.event_admin, events_type.event_type_name, event.id, 
                        event.is_approved, event.status,
                        total_amount.shagun_amount AS total_amount,
                        sender_count.sender_uid_count AS sender_count
                    FROM event
                    LEFT OUTER JOIN events_type ON event.event_type_id = events_type.id
                    LEFT OUTER JOIN (
                        SELECT event_id, SUM(shagun_amount) AS shagun_amount
                        FROM transaction_history
                        GROUP BY event_id
                    ) AS total_amount ON event.id = total_amount.event_id
                    LEFT OUTER JOIN (
                        SELECT event_id, COUNT(DISTINCT sender_uid) AS sender_uid_count
                        FROM transaction_history
                        GROUP BY event_id
                    ) AS sender_count ON event.id = sender_count.event_id
                    WHERE JSON_CONTAINS(event_admin, %(uid_json)s)
                    AND event.is_approved = 1 ORDER BY event.created_on DESC
                """

            # UID JSON data
            uid_json = json.dumps({'uid': uid})

            # Execute the first query for past events
            cursor.execute(sql_query_my_events, {'uid_json': uid_json})
            my_events = cursor.fetchall()

            invited_events_query = f"""
                        SELECT et.event_type_name, e.event_date, e.event_admin, e.id, egi.status, u_invited_by.phone, 
                        u_invited_by.name, u_invited_by.profile_pic
                        FROM event_guest_invite AS egi
                        LEFT JOIN users AS u ON u.phone = egi.invited_to
                        LEFT JOIN event AS e ON egi.event_id = e.id
                        LEFT JOIN events_type AS et ON e.event_type_id = et.id
                        LEFT JOIN users AS u_invited_by ON u_invited_by.uid = egi.invited_by
                        WHERE egi.invited_to = '{phone}' AND e.status = 1
                        ORDER BY egi.created_at DESC
                        LIMIT 5
                    """
            cursor.execute(invited_events_query)
            invited_events = cursor.fetchall()

            event_type_list_query = """SELECT * FROM events_type WHERE status=1"""
            cursor.execute(event_type_list_query)
            event_type_list = cursor.fetchall()

            return {
                "status": True,
                "my_events": responsegenerator.responseGenerator.generateResponse(my_events, EVENT_LIST),
                "invited_events": responsegenerator.responseGenerator.generateResponse(invited_events,
                                                                                       INVITED_EVENT_LIST),
                "event_type_list": responseGenerator.generateResponse(event_type_list, EVENT_TYPE_LIST)

            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def search_user_event(uid):
    try:
        with connection.cursor() as cursor:
            sql_query_upcoming_events = f"""
                        SELECT event.event_date, event.event_admin, events_type.event_type_name, event.id, 
                            event.is_approved, event.status, (SELECT phone FROM users WHERE uid = '{uid}') AS users
                        FROM event 
                        LEFT JOIN events_type ON event.event_type_id = events_type.id
                        WHERE JSON_CONTAINS(event_admin, %(uid_json)s) 
                        AND event.is_approved = 1 and event.status = 1 ORDER BY event.created_on DESC"""
            uid_json = json.dumps({'uid': uid})
            cursor.execute(sql_query_upcoming_events, {'uid_json': uid_json})
            upcoming_events = cursor.fetchall()

            return {
                "status": True,
                "upcoming_events": responsegenerator.responseGenerator.generateResponse(upcoming_events,
                                                                                        SEARCH_EVENT_LIST)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_all_event_list():
    try:
        with connection.cursor() as cursor:
            event_list_query = """SELECT e.event_date, e.event_admin, et.event_type_name, e.id, 
                                  e.is_approved, e.status, creator.name, updator.name, e.created_on, e.updated_on  
                                  FROM event AS e
                                    LEFT JOIN users AS creator ON e.created_by_uid = creator.uid
                                    LEFT JOIN users AS updator ON e.updated_by = updator.uid
                                    LEFT JOIN events_type AS et ON e.event_type_id = et.id 
                                  ORDER BY e.id DESC """
            cursor.execute(event_list_query)
            events = cursor.fetchall()
            for event in events:
                admins = json.loads(event[1])
                for admin in admins:
                    print(admin['uid'])

            return {
                "status": True,
                "event_list": responsegenerator.responseGenerator.generateResponse(events, ALL_EVENT_LIST)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def dashboard_search_event(search):
    try:
        with connection.cursor() as cursor:
            single_events_query = f"""
                                    SELECT event.event_date, event.event_admin, events_type.event_type_name, event.id, 
                                        event.is_approved, event.status
                                    FROM event 
                                    LEFT JOIN events_type ON event.event_type_id = events_type.id
                                    WHERE event.id LIKE '%%{search}%%' OR events_type.event_type_name LIKE '%%{search}%%' 
                                    OR LOWER(event.event_admin) LIKE LOWER('%%{search}%%') OR 
                                    event.event_date LIKE '%%{search}%%' ORDER BY event.created_on DESC"""
            cursor.execute(single_events_query)
            events = cursor.fetchall()
            return {
                "status": True,
                "event_list": responsegenerator.responseGenerator.generateResponse(events, ALL_EVENT_LIST)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_all_active_events():
    try:
        with connection.cursor() as cursor:
            active_events_query = f"""SELECT event.event_date, event.event_admin, events_type.event_type_name, event.id, 
            event.is_approved, event.status  FROM event LEFT JOIN events_type ON event.event_type_id = events_type.id 
            WHERE event.status= '{True}' ORDER BY event.created_on DESC"""
            cursor.execute(active_events_query)
            events = cursor.fetchall()
            return {
                "msg": events
            }
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_city_list_for_user():
    try:
        with connection.cursor() as cursor:
            get_location_query = """SELECT * FROM locations WHERE status=1"""
            cursor.execute(get_location_query)
            locations_list = cursor.fetchall()

            return {
                "status": True,
                "city_list": responseGenerator.generateResponse(locations_list, ACTIVE_LOCATIONS_LIST)

            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def set_event_status(event_id, status, approver):
    try:
        with connection.cursor() as cursor:
            event_status_query = "UPDATE event SET is_approved = %s WHERE id = %s"
            values = (status, event_id)
            cursor.execute(event_status_query, values)
            if status == 1:
                event_approve_query = f"UPDATE event SET approved_by = '{approver}' WHERE id = '{event_id}'"
                cursor.execute(event_approve_query)
            return {
                "status": True,
                "message": "Event Status changed successfully"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301

    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_event_admins(e_id):
    try:
        with connection.cursor() as cursor:
            active_events_query = f"""SELECT event_admin FROM event WHERE id = '{e_id}' """
            cursor.execute(active_events_query)
            admins = cursor.fetchone()
            return {
                "admins": json.loads(admins[0])
            }
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def event_admin(event_id):
    try:
        with connection.cursor() as cursor:
            event_admin_query = f"""SELECT event.event_admin FROM event
                        WHERE  id = '{event_id}'"""
            cursor.execute(event_admin_query)
            admin = cursor.fetchone()
            event_admins = json.loads(admin[0])
            for item in event_admins:
                uid = item["uid"]
                phone_query = f"""SELECT phone FROM users
                                        WHERE  uid = '{uid}'"""
                cursor.execute(phone_query)
                phone = cursor.fetchone()
                item["qr_code"] = str(event_id) + "_" + phone[0]

            update_qr_sql = f"""UPDATE event SET event_admin = '{json.dumps(event_admins)}' WHERE id = '{event_id}' """
            cursor.execute(update_qr_sql)
            return {
                "status": True,
                "msg": event_admins
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def save_event_guest_invite(invited_by, invited_to, e_id, invite_message):
    try:
        with connection.cursor() as cursor:
            invite_query = """
                INSERT INTO event_guest_invite (invited_by, invited_to, event_id, invite_message, created_at) 
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                invited_by = VALUES(invited_by), invite_message = VALUES(invite_message)
            """
            data_list = [(invited_by, invited_to, e_id, invite_message, getIndianTime()) for invited_to in invited_to]
            cursor.executemany(invite_query, data_list)

            event_name_query = f"""SELECT et.event_type_name FROM event AS e
                        LEFT JOIN events_type AS et ON e.event_type_id = et.id
                        WHERE  e.id = '{e_id}'"""
            cursor.execute(event_name_query)
            event_name = cursor.fetchone()

            inviter_name_query = f"""SELECT name FROM users WHERE  uid = '{invited_by}'"""
            cursor.execute(inviter_name_query)
            invited_by = cursor.fetchone()

            user_query = f"""SELECT name, fcm_token, uid FROM users WHERE phone IN %s"""
            cursor.execute(user_query, (invited_to,))
            results = cursor.fetchall()
            for row in results:
                name, fcm_token, uid = row
                invite_notification_query = f"""INSERT INTO notification (uid, type, title, message, created_on) 
                                        VALUES ('{uid}', 'invite',
                                        '{invited_by[0]} has invited you to {event_name[0]}',
                                        '{invited_by[0]} has invited you to {event_name[0]}',
                                        '{getIndianTime()}')"""
                cursor.execute(invite_notification_query)
                title = f"""{invited_by[0]} has invited you to {event_name[0]}"""
                send_push_notification(fcm_token, title, invite_message)
            return {"status": True, "message": "Invitation sent Successfully"}, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301

    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_invited_users_list(e_id):
    try:
        with connection.cursor() as cursor:
            active_events_query = f"""SELECT invited_to, u.name, invite_message	, created_at 
            FROM event_guest_invite AS eg
            LEFT JOIN users AS u ON eg.invited_by = u.uid
            WHERE eg.event_id = '{e_id}' ORDER BY eg.created_at DESC"""
            cursor.execute(active_events_query)
            invited_users = cursor.fetchall()
            return {
                "invited_list": responsegenerator.responseGenerator.generateResponse(invited_users, INVITED_USERS_LIST)
            }
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_my_invited_event_list(uid):
    try:
        with connection.cursor() as cursor:
            invited_events_query = f"""
                SELECT et.event_type_name, e.event_date, e.event_admin, e.id, egi.status, u_invited_by.phone, 
                u_invited_by.name, u_invited_by.profile_pic
                FROM event_guest_invite AS egi
                LEFT JOIN users AS u ON u.phone = egi.invited_to
                LEFT JOIN event AS e ON egi.event_id = e.id
                LEFT JOIN events_type AS et ON e.event_type_id = et.id
                LEFT JOIN users AS u_invited_by ON u_invited_by.uid = egi.invited_by
                WHERE egi.invited_to = (SELECT phone FROM users WHERE uid = '{uid}') AND e.status = 1
                ORDER BY egi.created_at DESC
            """
            cursor.execute(invited_events_query)
            invited_events = cursor.fetchall()
            return {
                "invited_list": responsegenerator.responseGenerator.generateResponse(invited_events,
                                                                                     INVITED_EVENTS_LIST)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_my_notifications_list(uid):
    try:
        with connection.cursor() as cursor:
            notification_query = f""" SELECT * FROM notification WHERE uid = '{uid}' ORDER BY created_on DESC"""
            cursor.execute(notification_query)
            notification_list = cursor.fetchall()
            return {
                "notification_list": responsegenerator.responseGenerator.generateResponse(notification_list,
                                                                                          NOTIFICATION_LIST)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301
