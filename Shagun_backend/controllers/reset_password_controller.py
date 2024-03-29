import json

import bcrypt
import pymysql
from django.db import connection
import random
import string
import requests
import json
import os
from django.http import JsonResponse

from Shagun_backend.controllers.credentials import get_credentials


def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    random_pwd = ''.join(random.choice(characters) for _ in range(length))

    return random_pwd


def reset_password(email, user):
    try:
        with connection.cursor() as cursor:
            new_pwd = generate_random_string()
            hashed_password = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if user == 'printer_login' or user == 'manage_printers':
                printer_check_query = f"""SELECT id, status FROM printer 
                                                    WHERE email = '{email}' """
                cursor.execute(printer_check_query)
                result = cursor.fetchone()
                if result is not None and result[1] == 1:
                    credentials = get_credentials()
                    url = credentials.get('emailjs_url')
                    data = {
                        'service_id': credentials.get('emailjs_service_id'),
                        'template_id': credentials.get('emailjs_template_id'),
                        'user_id': credentials.get('emailjs_user_id'),
                        'template_params': {
                            'to_email': email,
                            'new_password': new_pwd,
                            'g-recaptcha-response': credentials.get('emailjs_grecaptcha_response')
                        }
                    }

                    headers = {'Content-Type': 'application/json'}

                    email_response = requests.post(url, data=json.dumps(data), headers=headers)
                    if email_response.status_code == 200:
                        sql_query = f"""UPDATE printer SET printer_password = '{hashed_password}' WHERE email = '{email}' """
                        cursor.execute(sql_query)
                        return {
                            "status": True,
                            "message": "Password reset successful. We have sent you an email with new password, please click OK to login using new password"
                        }, 200
                    else:
                        return {
                            "status": False,
                            "message": "Failed to send the new password. Please try again or contact your admin if you are facing the issue continiously"
                        }, 200


                elif result is not None and result[1] == 0:
                    return {
                        "status": False,
                        "message": "Password reset Failed due to Inactive Account. Please contact your Admin"
                    }, 200

                else:
                    return {
                        "status": False,
                        "message": "Please enter the valid email to reset the password"
                    }, 200

            else:
                user_check_query = f"""SELECT id, status FROM users WHERE email = '{email}' """
                cursor.execute(user_check_query)
                result = cursor.fetchone()
                if result is not None and result[1] == 1:
                    credentials = get_credentials()
                    url = credentials.get('emailjs_url')
                    data = {
                        'service_id': credentials.get('emailjs_service_id'),
                        'template_id': credentials.get('emailjs_template_id'),
                        'user_id': credentials.get('emailjs_user_id'),
                        'template_params': {
                            'to_email': email,
                            'new_password': new_pwd,
                            'g-recaptcha-response': credentials.get('emailjs_grecaptcha_response')
                        }
                    }

                    headers = {'Content-Type': 'application/json'}

                    email_response = requests.post(url, data=json.dumps(data), headers=headers)
                    if email_response.status_code == 200:
                        sql_query = f"""UPDATE users SET password = '{hashed_password}' WHERE email = '{email}' """
                        cursor.execute(sql_query)
                        return {
                            "status": True,
                            "message": "Password reset successful. We have sent you an email with new password, please click OK to login using new password"
                        }, 200
                    else:
                        return {
                            "status": False,
                            "message": "Failed to send the new password. Please try again or contact your admin if you are facing the issue continiously"
                        }, 200


                elif result is not None and result[1] == 0:
                    return {
                        "status": False,
                        "message": "Password reset Failed due to Inactive Account. Please contact your Admin"
                    }, 200
                else:
                    return {
                        "status": False,
                        "message": "Please enter the valid email to reset the password"
                    }, 200



    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301

def admin_reset_password(email, user):
    try:
        with connection.cursor() as cursor:
            new_pwd = generate_random_string()
            hashed_password = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if user == 'printer_login' or user == 'manage_printers':
                printer_check_query = f"""SELECT id, status FROM printer 
                                                    WHERE email = '{email}' """
                cursor.execute(printer_check_query)
                result = cursor.fetchone()
                if result is not None and result[1] == 1:
                    credentials = get_credentials()
                    url = credentials.get('emailjs_url')
                    data = {
                        'service_id': credentials.get('emailjs_service_id'),
                        'template_id': credentials.get('emailjs_template_id'),
                        'user_id': credentials.get('emailjs_user_id'),
                        'template_params': {
                            'to_email': email,
                            'new_password': new_pwd,
                            'g-recaptcha-response': credentials.get('emailjs_grecaptcha_response')
                        }
                    }

                    headers = {'Content-Type': 'application/json'}

                    email_response = requests.post(url, data=json.dumps(data), headers=headers)
                    if email_response.status_code == 200:
                        sql_query = f"""UPDATE printer SET printer_password = '{hashed_password}' WHERE email = '{email}' """
                        cursor.execute(sql_query)
                        return {
                            "status": True,
                            "message": f"Password reset successful. We have sent an email to {email} with new password."
                        }, 200
                    else:
                        return {
                            "status": False,
                            "message": f"Failed to send the new password to {email}. Please try again or contact your admin if you are facing the issue continiously"
                        }, 200


                elif result is not None and result[1] == 0:
                    return {
                        "status": False,
                        "message": f"Password reset Failed for {email} due to Inactive Account. Please contact your Admin"
                    }, 200

                else:
                    return {
                        "status": False,
                        "message": "Please enter the valid email to reset the password"
                    }, 200

            else:
                user_check_query = f"""SELECT id, status FROM users WHERE email = '{email}' """
                cursor.execute(user_check_query)
                result = cursor.fetchone()
                if result is not None and result[1] == 1:
                    credentials = get_credentials()
                    url = credentials.get('emailjs_url')
                    data = {
                        'service_id': credentials.get('emailjs_service_id'),
                        'template_id': credentials.get('emailjs_template_id'),
                        'user_id': credentials.get('emailjs_user_id'),
                        'template_params': {
                            'to_email': email,
                            'new_password': new_pwd,
                            'g-recaptcha-response': credentials.get('emailjs_grecaptcha_response')
                        }
                    }

                    headers = {'Content-Type': 'application/json'}

                    email_response = requests.post(url, data=json.dumps(data), headers=headers)
                    if email_response.status_code == 200:
                        sql_query = f"""UPDATE users SET password = '{hashed_password}' WHERE email = '{email}' """
                        cursor.execute(sql_query)
                        return {
                            "status": True,
                            "message": f"Password reset successful. We have sent an email to {email} with new password."
                        }, 200
                    else:
                        return {
                            "status": False,
                            "message": f"Failed to send the new password to {email}. Please try again or contact your admin if you are facing the issue continiously"
                        }, 200


                elif result is not None and result[1] == 0:
                    return {
                        "status": False,
                        "message": "Password reset Failed for {email} due to Inactive Account. Please contact your Admin"
                    }, 200
                else:
                    return {
                        "status": False,
                        "message": "Please enter the valid email to reset the password"
                    }, 200



    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301