import pymysql
from django.db import connection

from Shagun_backend.util import responsegenerator
from Shagun_backend.util.constants import ALL_PRINTERS_DATA, DELIVERY_VENDOR_DATA


def add_vendor(vendor_obj):
    try:
        with connection.cursor() as cursor:
            add_printer_query = """INSERT INTO delivery_vendors (delivery_vendor_name, city, address, 
                                   gst_no, delivery_vendor_owner, contact_number, created_by) 
                                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(add_printer_query, [vendor_obj.delivery_vendor_name, vendor_obj.city, vendor_obj.address,
                                               vendor_obj.gst_no, vendor_obj.delivery_vendor_owner,
                                               vendor_obj.contact_number, vendor_obj.created_by])
            return {
                "status": True,
                "Vendor": "Vendor added successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def enable_disable_vendor(vendor_id, status):
    try:
        with connection.cursor() as cursor:
            disable_query = "UPDATE delivery_vendors SET status = %s WHERE id = %s"
            values = (status, vendor_id)
            cursor.execute(disable_query, values)
            return {
                "status": True,
                "vendor_status": "vendor  status changed successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def dashboard_search_delivery_vendor(search):
    try:
        with connection.cursor() as cursor:
            delivery_vendor_data_query = f""" SELECT p.id, p.delivery_vendor_name, l.city_name, p.address, p.status, p.gst_no, 
            p.delivery_vendor_owner, p.contact_number FROM delivery_vendors AS p
            LEFT JOIN locations AS l ON p.city = l.id 
            WHERE (p.id LIKE '%{search}%' OR delivery_vendor_name LIKE '%{search}%' OR delivery_vendor_owner LIKE '%{search}%'
            OR contact_number LIKE '%{search}%' )"""
            cursor.execute(delivery_vendor_data_query)
            delivery_vendor_data = cursor.fetchall()
            return {
                "status": True,
                "delivery_vendor_data": responsegenerator.responseGenerator.generateResponse(delivery_vendor_data, ALL_PRINTERS_DATA)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def dashboard_search_delivery_vendor_status(status):
    try:
        with connection.cursor() as cursor:
            delivery_vendor_status_query = f""" SELECT p.id, p.delivery_vendor_name, l.city_name, p.address, p.status, p.gst_no, 
            p.delivery_vendor_owner, p.contact_number FROM delivery_vendors AS p
            LEFT JOIN locations AS l ON p.city = l.id WHERE p.status = '{status}'"""
            cursor.execute(delivery_vendor_status_query)
            delivery_vendor_data = cursor.fetchall()
            return {
                "status": True,
                "delivery_vendor_data": responsegenerator.responseGenerator.generateResponse(delivery_vendor_data, ALL_PRINTERS_DATA)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def enable_disable_delivery_vendor(pid, pstatus):
    try:
        with connection.cursor() as cursor:
            disable_query = "UPDATE delivery_vendors SET status = %s WHERE id = %s"
            values = (pstatus, pid)
            cursor.execute(disable_query, values)
            return {
                "status": True,
                "msg": "delivery vendor  status changed successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301



def get_delivery_vendor():
    try:
        with connection.cursor() as cursor:
            printers_data_query = f""" SELECT p.id, p.delivery_vendor_name, l.city_name, p.address, p.status, p.gst_no, 
            p.delivery_vendor_owner, p.contact_number FROM delivery_vendors AS p
            LEFT JOIN locations AS l ON p.city = l.id"""
            cursor.execute(printers_data_query)
            delivery_vendor_data = cursor.fetchall()
            return {
                "status": True,
                "delivery_vendor_data": responsegenerator.responseGenerator.generateResponse(delivery_vendor_data, ALL_PRINTERS_DATA)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def edit_delivery_vendor(vendor_id):
    try:
        with connection.cursor() as cursor:
            printers_data_query = f""" SELECT * FROM delivery_vendors WHERE id = '{vendor_id}' """
            cursor.execute(printers_data_query)
            delivery_vendor_data = cursor.fetchone()
            return {
                "status": True,
                "delivery_vendor_data": responsegenerator.responseGenerator.generateResponse(delivery_vendor_data, DELIVERY_VENDOR_DATA)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def update_vendor(vendor_obj):
    try:
        with connection.cursor() as cursor:
            update_vendor_query = f"""
                        UPDATE  delivery_vendors SET delivery_vendor_name = '{vendor_obj.delivery_vendor_name}',
                        city = '{vendor_obj.city}', address = '{vendor_obj.address}', gst_no = '{vendor_obj.gst_no}', 
                        delivery_vendor_owner = '{vendor_obj.delivery_vendor_owner}', 
                        contact_number = '{vendor_obj.contact_number}', created_by = '{vendor_obj.created_by}'
                         WHERE id = '{vendor_obj.id}' 
                        """
            cursor.execute(update_vendor_query)
            return {
                "status": True,
                "Vendor": "Vendor updated successfully"
            }, 200
    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301

