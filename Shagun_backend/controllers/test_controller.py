import json

import pymysql
from django.db import connection

from Shagun_backend.util import responsegenerator
from Shagun_backend.util.constants import EVENT_ADMIN


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
                print(uid)
                print(phone[0])
                item["qr_code"] = str(event_id)+"_"+phone[0]
                print(item)

            print(event_admins)

            update_qr_sql = f"""UPDATE event SET event_admin = '{json.dumps(event_admins)}' WHERE id = '{event_id}' """
            cursor.execute(update_qr_sql)
            return {
                "status": True,
                "msg": event_admins
                # "event_admin": responsegenerator.responseGenerator.generateResponse(admin, EVENT_ADMIN)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301
