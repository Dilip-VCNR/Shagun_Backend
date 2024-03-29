import hashlib

import pymysql
from django.db import connection

from Shagun_backend.controllers.event_controller import send_push_notification
from Shagun_backend.util.constants import *
from Shagun_backend.util.responsegenerator import responseGenerator


def add_transaction_history(transaction_obj):
    try:
        with connection.cursor() as cursor:
            transaction_history_query = f"""INSERT INTO transaction_history (sender_uid, receiver_uid, 
            transaction_amount, shagun_amount, greeting_card_id, transaction_fee, delivery_fee, transaction_id, 
            payment_status, event_id, status, created_on, gifter_name,greeting_card_price) 
            VALUES ('{transaction_obj.uid}', '{transaction_obj.receiver_uid}', 
            '{transaction_obj.transaction_amount}', '{transaction_obj.shagun_amount}', '{transaction_obj.greeting_card_id}',
            '{transaction_obj.transaction_fee}', '{transaction_obj.delivery_fee}', '{transaction_obj.transaction_id}',
            '{transaction_obj.payment_status}', '{transaction_obj.event_id}', {transaction_obj.status}, '{getIndianTime()}', 
            '{transaction_obj.gifter_name}','{transaction_obj.greeting_card_price}')"""

            cursor.execute(transaction_history_query)
            transaction_id = cursor.lastrowid

            event_type_query = f"""SELECT et.event_type_name FROM event AS e
                                            LEFT JOIN events_type AS et ON e.event_type_id = et.id
                                             WHERE e.id = '{transaction_obj.event_id}' """
            cursor.execute(event_type_query)
            event_type = cursor.fetchone()

            receiver_name_query = f"""SELECT name FROM users WHERE uid = '{transaction_obj.receiver_uid}' """
            cursor.execute(receiver_name_query)
            recv_name = cursor.fetchone()

            reciever_notification_query = f"""INSERT INTO notification (uid, type, title, message, created_on) 
            VALUES ('{transaction_obj.receiver_uid}', 'Shagun',
            '{transaction_obj.gifter_name} sent you Shagun amount: {transaction_obj.shagun_amount} ',
            'For your {event_type[0]} event',
            '{getIndianTime()}')"""
            cursor.execute(reciever_notification_query)

            sender_notification_query = f"""INSERT INTO notification (uid, type, title, message,created_on) 
            VALUES ('{transaction_obj.uid}', 'Shagun','Shagun Amount sent to {recv_name[0]}', 
            'You have sent Shagun amount: {transaction_obj.shagun_amount} to {recv_name[0]} for the {event_type[0]} event',
            '{getIndianTime()}')"""
            cursor.execute(sender_notification_query)

            printer_query = f"""SELECT printer_id FROM event 
                                 WHERE id = '{transaction_obj.event_id}' """
            cursor.execute(printer_query)
            printer = cursor.fetchone()

            printer_jobs_query = f""" INSERT INTO print_jobs(transaction_id, printer_id, card_id, status,
             created_on, last_modified, billing_amount, event_id, wish)
              VALUES('{transaction_id}', '{printer[0]}', '{transaction_obj.greeting_card_id}',
               1,'{getIndianTime()}', '{getIndianTime()}', '{transaction_obj.greeting_card_price}', '{transaction_obj.event_id}', '{transaction_obj.wish}' )"""

            cursor.execute(printer_jobs_query)

            add_printer_query = """INSERT INTO order_status (transaction_id, status, created_on) 
                                                         VALUES (%s, %s, %s)"""
            cursor.execute(add_printer_query, [transaction_id, 1, getIndianTime()])

            sender_notification_query = f"""INSERT INTO notification (uid, type, title, message, created_on) 
                        VALUES ('{transaction_obj.uid}', 'Transaction','Order {transaction_id} status: Job Created', 
                        'Your transaction is created and pending for further processing.',
                        '{getIndianTime()}')"""
            cursor.execute(sender_notification_query)

            fcm_query = f"""SELECT fcm_token FROM users 
                                             WHERE uid = '{transaction_obj.uid}' """
            cursor.execute(fcm_query)
            fcm_token = cursor.fetchone()
            title = f"Order {transaction_id} status: Job Created"
            message = "Your transaction is created and pending for further processing."
            send_push_notification(fcm_token[0], title, message)

            receiver_fcm_query = f"""SELECT fcm_token FROM users 
                                             WHERE uid = '{transaction_obj.receiver_uid}' """
            cursor.execute(receiver_fcm_query)
            recv_fcm_token = cursor.fetchone()
            title = f"{transaction_obj.gifter_name} sent you Shagun amount: {transaction_obj.shagun_amount}"
            message = f"For your {event_type[0]} event"
            send_push_notification(recv_fcm_token[0], title, message)

            return {
                "status": True,
                "msg": "Transaction records added"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def event_settlement(event_id):
    try:
        with connection.cursor() as cursor:
            event_settlement_query = f"""
                SELECT SUM(CASE WHEN th.is_settled = 0 THEN shagun_amount ELSE 0 END) 
                AS total_shagun_amount, 
                SUM(CASE WHEN th.is_settled <> 0 THEN shagun_amount ELSE 0 END)
                AS settled_amount,
                SUM(shagun_amount) AS total_received_amount 
                FROM transaction_history th
                WHERE th.event_id = '{event_id}' ORDER BY th.created_on DESC;
            """
            cursor.execute(event_settlement_query)
            amount = cursor.fetchone()

            return {
                "status": True,
                "total_shagun": amount[2],
                "settled_amount": amount[1],
                "unsettled_shagun_amount": amount[0]
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_sent_gift(gift_data_obj):
    if gift_data_obj.month != '1':
        month_filter = f"DATE_FORMAT(th.created_on, '%Y-%m') = '{gift_data_obj.month}'"
    else:
        month_filter = "1"
    try:
        with connection.cursor() as cursor:
            events_list_query = """ SELECT id, event_type_name from events_type """
            cursor.execute(events_list_query)
            events_data = cursor.fetchall()

            sent_gift_query = f"""
                SELECT th.receiver_uid, th.sender_uid, th.shagun_amount, th.transaction_amount,
                    th.transaction_fee, th.delivery_fee, th.created_on, gc.card_price, et.event_type_name, th.id, 
                    CASE WHEN th.is_settled <> 0 THEN True ELSE False END AS settlement_status,
                    (SELECT SUM(shagun_amount) FROM transaction_history WHERE sender_uid = '{gift_data_obj.uid}')
                     AS total_amount, u.name, bd.bank_name, bd.bank_logo, bd.account_number, u.profile_pic, pj.wish, 
                     th.gifter_name
                FROM transaction_history AS th
                LEFT JOIN users As u ON th.receiver_uid = u.uid
                LEFT JOIN event AS ev ON th.event_id = ev.id
                LEFT JOIN events_type AS et ON ev.event_type_id = et.id
                LEFT JOIN greeting_cards AS gc ON th.greeting_card_id = gc.id
                LEFT JOIN bank_details AS bd ON th.reciever_bank_id = bd.id
                LEFT JOIN print_jobs AS pj ON th.id = pj.transaction_id
                WHERE th.sender_uid = '{gift_data_obj.uid}'AND et.event_type_name LIKE '{gift_data_obj.type}' AND 
                ({month_filter}) ORDER BY th.created_on DESC"""
            cursor.execute(sent_gift_query)
            sent_gifts = cursor.fetchall()

            events_list = responseGenerator.generateResponse(events_data, EVENT_TYPE_LIST)
            total_gift_sent, sent_gift_list = responseGenerator.generateResponse(sent_gifts, GIFT_SENT)
            return {
                "status": True,
                "events_list": events_list,
                "total_gift_sent": total_gift_sent,
                "sent_gifts": sent_gift_list
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_received_gift(gift_data_obj):
    if gift_data_obj.month != '1':
        # Use the provided month in the query
        month_filter = f"DATE_FORMAT(th.created_on, '%Y-%m') = '{gift_data_obj.month}'"
    else:
        # If 'month' is not provided, include all records (no filtering by month)
        month_filter = "1"
    try:
        with connection.cursor() as cursor:
            events_list_query = """SELECT id, event_type_name from events_type"""
            cursor.execute(events_list_query)
            events_data = cursor.fetchall()

            sent_gift_query = f"""
                SELECT th.receiver_uid, th.sender_uid, th.shagun_amount, th.transaction_amount,
                    th.transaction_fee, th.delivery_fee, th.created_on, gc.card_price, et.event_type_name, th.id, 
                    CASE WHEN th.is_settled <> 0 THEN True ELSE False END AS settlement_status,
                    (SELECT SUM(shagun_amount) FROM transaction_history WHERE receiver_uid = '{gift_data_obj.uid}') 
                    AS total_amount, u.name, bd.bank_name, bd.bank_logo, bd.account_number, u.profile_pic, pj.wish,
                    th.gifter_name
                FROM transaction_history AS th
                LEFT JOIN users As u ON th.sender_uid = u.uid
                LEFT JOIN event AS ev ON th.event_id = ev.id
                LEFT JOIN events_type AS et ON ev.event_type_id = et.id
                LEFT JOIN greeting_cards AS gc ON th.greeting_card_id = gc.id
                LEFT JOIN bank_details AS bd ON th.reciever_bank_id = bd.id
                LEFT JOIN print_jobs AS pj ON th.id = pj.transaction_id
                WHERE th.receiver_uid = '{gift_data_obj.uid}' AND et.event_type_name LIKE '{gift_data_obj.type}' AND 
                ({month_filter}) ORDER BY th.created_on DESC"""
            cursor.execute(sent_gift_query)
            received_gifts = cursor.fetchall()
            events_list = responseGenerator.generateResponse(events_data, EVENT_TYPE_LIST)
            total_gift_received, received_gift_list = responseGenerator.generateResponse(received_gifts, GIFT_SENT)

            return {
                "status": True,
                "events_list": events_list,
                "total_received_gifts": total_gift_received,
                "received_gifts": received_gift_list
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_received_gift_for_event(uid, eid):
    try:
        with connection.cursor() as cursor:
            sent_gift_query = f"""
                SELECT th.receiver_uid, th.sender_uid, th.shagun_amount, th.transaction_amount,
                    th.transaction_fee, th.delivery_fee, th.created_on, gc.card_price, et.event_type_name, th.id, 
                    CASE WHEN th.is_settled <> 0 THEN True ELSE False END AS settlement_status,
                    (SELECT SUM(shagun_amount) FROM transaction_history WHERE receiver_uid = '{uid}' AND event_id = '{eid}') 
                    AS total_amount, u.name, bd.bank_name, bd.bank_logo, bd.account_number, u.profile_pic, pj.wish,
                    th.gifter_name
                FROM transaction_history AS th
                LEFT JOIN users As u ON th.sender_uid = u.uid
                LEFT JOIN event AS ev ON th.event_id = ev.id
                LEFT JOIN events_type AS et ON ev.event_type_id = et.id
                LEFT JOIN greeting_cards AS gc ON th.greeting_card_id = gc.id
                LEFT JOIN bank_details AS bd ON th.reciever_bank_id = bd.id
                LEFT JOIN print_jobs AS pj ON th.id = pj.transaction_id
                WHERE th.receiver_uid = '{uid}' AND th.event_id = '{eid}' ORDER BY th.created_on DESC"""
            cursor.execute(sent_gift_query)
            received_gifts = cursor.fetchall()
            total_gift_received, received_gift_list = responseGenerator.generateResponse(received_gifts, GIFT_SENT)

            return {
                "status": True,
                "total_received_gifts": total_gift_received,
                "received_gifts": received_gift_list
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_transaction_list(event_id, status):
    try:
        with connection.cursor() as cursor:
            track_order_query = f"""
                SELECT th.*, e.event_date, et.event_type_name, sender.name, receiver.name, 
                       bk.bank_name, os.created_on, bk.account_number, receiver.phone,
                       CASE WHEN EXISTS (
                           SELECT 1
                           FROM bank_details AS active_bank
                           WHERE active_bank.uid = receiver.uid AND active_bank.status = 1
                       ) THEN 1 ELSE 0 END AS has_active_bank
                FROM transaction_history AS th
                LEFT JOIN event AS e ON th.event_id = e.id
                LEFT JOIN events_type AS et ON e.event_type_id = et.id
                LEFT JOIN users AS sender ON th.sender_uid = sender.uid
                LEFT JOIN users AS receiver ON th.receiver_uid = receiver.uid
                LEFT JOIN bank_details AS bk ON th.reciever_bank_id = bk.id
                LEFT JOIN (
                    SELECT transaction_id, MAX(CASE WHEN status = 6 THEN created_on END) AS created_on
                    FROM order_status
                    GROUP BY transaction_id
                ) AS os ON th.id = os.transaction_id
                WHERE th.event_id = '{event_id}' AND th.is_settled LIKE '{status}'
                ORDER BY th.created_on DESC

            """
            cursor.execute(track_order_query)
            track = cursor.fetchall()

            return {
                "status": True,
                "message": "Transaction Completed",
                "transactions": responseGenerator.generateResponse(track, Transaction_DATA)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def search_transaction_list(event_id, search):
    try:
        with connection.cursor() as cursor:
            track_order_query = f""" SELECT th.*, e.event_date, et.event_type_name,sender.name, receiver.name
            FROM transaction_history AS th
            LEFT JOIN event As e ON th.event_id = e.id
            LEFT JOIN events_type As et ON e.event_type_id = et.id
            LEFT JOIN users As sender ON th.sender_uid = sender.uid
            LEFT JOIN users As receiver ON th.receiver_uid = receiver.uid
            WHERE th.event_id = '{event_id}' AND (th.transaction_id LIKE '%%{search}%%' OR th.gifter_name LIKE '%%{search}%%' 
                                    OR LOWER(sender.name) LIKE LOWER('%%{search}%%')) ORDER BY th.created_on DESC """
            cursor.execute(track_order_query)
            track = cursor.fetchall()
            return {
                "status": True,
                "transactions": responseGenerator.generateResponse(track, Transaction_DATA)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def settle_payment(transactions_list, settled_by):
    try:
        with connection.cursor() as cursor:
            transactions_string = ', '.join(transactions_list)
            settlement_data_query = f"""SELECT th.receiver_uid, th.shagun_amount, u.name AS sender_name, th.id 
                                        FROM transaction_history AS th
                                        LEFT JOIN users AS u ON u.uid = th.sender_uid
                                        WHERE th.id IN ({transactions_string})"""
            cursor.execute(settlement_data_query)
            settlement_data = cursor.fetchall()
            user_totals = {}

            for receiver, amount, sender_name, tid in settlement_data:
                if receiver in user_totals:
                    user_totals[receiver]['amount'] += amount
                    user_totals[receiver]['sender_name'] = sender_name
                    user_totals[receiver].setdefault('tid', []).append(tid)
                else:
                    user_totals[receiver] = {'amount': amount, 'sender_name': sender_name, 'tid': [tid]}

            for receiver, data in user_totals.items():
                total_amount = data['amount']
                sender_name = data['sender_name']
                trans_id = data['tid']
                bank_data_query = f"""SELECT bk.bank_name, bk.ifsc_code, bk.account_holder_name, bk.account_number,
                                        u.name, u.fcm_token, bk.id FROM bank_details AS bk 
                                        LEFT JOIN users AS u ON bk.uid = u.uid 
                                        WHERE bk.uid = '{receiver}' AND bk.status = 1 """
                cursor.execute(bank_data_query)
                bank_data = cursor.fetchall()
                for row in bank_data:
                    bank_name, ifsc_code, account_holder_name, account_number, receiver_name, fcm_token, bkid = row
                    transactions_id_list = ','.join(map(str, trans_id))
                    track_order_query = f"""UPDATE transaction_history SET is_settled = 1, settled_by = '{settled_by}',
                                                        reciever_bank_id = {bkid} WHERE id IN ({transactions_id_list}) """
                    cursor.execute(track_order_query)

                    invite_notification_query = f"""INSERT INTO notification (uid, type, title, message, created_on) 
                                                    VALUES ('{receiver}', 'shagun',
                                                    'Shagun amount {total_amount} credited by {sender_name}',
                                                    'Shagun amount of {total_amount} INR has been successfully transferred to {bank_name} Bank for the account ending with {'*' * (len(str(account_number)) - 4) + str(account_number)[-4:]}',
                                                    '{getIndianTime()}')"""
                    cursor.execute(invite_notification_query)
                    title = f"""Shagun amount {total_amount} credited from {sender_name}"""
                    message = f""" Shagun amount of {total_amount} INR has been successfully transferred to {bank_name} Bank for the account ending with {'*' * (len(str(account_number)) - 4) + str(account_number)[-4:]} """
                    send_push_notification(fcm_token, title, message)

        return {
            "status": True,
            "message": "Amount Transfer Completed",
        }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def update_transactions(transactions_list, settled_by):
    try:
        with connection.cursor() as cursor:
            transactions_string = ', '.join(transactions_list)
            # track_order_query = f"""UPDATE transaction_history SET is_settled = 1, settled_by = '{settled_by}'
            #                         WHERE id IN ({transactions_string})"""
            # cursor.execute(track_order_query)

            sql = "INSERT INTO order_status (transaction_id, status,created_on) VALUES (%s, %s, %s)"
            values = [(transaction_id, 6, getIndianTime()) for transaction_id in transactions_list]
            cursor.executemany(sql, values)

            return {
                "status": True,
                "message": "Settlement Completed"
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def get_transaction_track(tid):
    try:
        with connection.cursor() as cursor:
            track_order_query = f""" SELECT * from order_status WHERE transaction_id = {tid} """
            cursor.execute(track_order_query)
            track = cursor.fetchall()
            return {
                "status": True,
                "track_transaction": responseGenerator.generateResponse(track, TRACK_ORDER)
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def search_sent_gift(gift_data_obj):
    try:
        with connection.cursor() as cursor:
            events_list_query = """ SELECT id, event_type_name from events_type """
            cursor.execute(events_list_query)
            events_data = cursor.fetchall()

            sent_gift_query = f"""
                SELECT th.receiver_uid, th.sender_uid, th.shagun_amount, th.transaction_amount,
                    th.transaction_fee, th.delivery_fee, th.created_on, gc.card_price, et.event_type_name, th.id, 
                    CASE WHEN th.is_settled <> 0 THEN True ELSE False END AS settlement_status,
                    (SELECT SUM(shagun_amount) FROM transaction_history WHERE sender_uid = '{gift_data_obj.uid}')
                     AS total_amount, u.name, bd.bank_name, bd.bank_logo, bd.account_number, u.profile_pic, pj.wish,
                     th.gifter_name
                FROM transaction_history AS th
                LEFT JOIN users As u ON th.receiver_uid = u.uid
                LEFT JOIN event AS ev ON th.event_id = ev.id
                LEFT JOIN events_type AS et ON ev.event_type_id = et.id
                LEFT JOIN greeting_cards AS gc ON th.greeting_card_id = gc.id
                LEFT JOIN bank_details AS bd ON th.reciever_bank_id = bd.id
                LEFT JOIN print_jobs AS pj ON th.id = pj.transaction_id
                WHERE th.sender_uid = '{gift_data_obj.uid}' 
                AND ( u.name LIKE '%{gift_data_obj.search}%' OR u.phone LIKE '%{gift_data_obj.search}%') 
                ORDER BY th.created_on DESC"""
            cursor.execute(sent_gift_query)
            sent_gifts = cursor.fetchall()

            events_list = responseGenerator.generateResponse(events_data, EVENT_TYPE_LIST)
            total_gift_sent, sent_gift_list = responseGenerator.generateResponse(sent_gifts, GIFT_SENT)
            return {
                "status": True,
                "events_list": events_list,
                "total_gift_sent": total_gift_sent,
                "sent_gifts": sent_gift_list
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301


def search_received_gift(gift_data_obj):
    try:
        with connection.cursor() as cursor:
            events_list_query = """SELECT id, event_type_name from events_type"""
            cursor.execute(events_list_query)
            events_data = cursor.fetchall()

            sent_gift_query = f"""
                SELECT th.receiver_uid, th.sender_uid, th.shagun_amount, th.transaction_amount,
                    th.transaction_fee, th.delivery_fee, th.created_on, gc.card_price, et.event_type_name, th.id, 
                    CASE WHEN th.is_settled <> 0 THEN True ELSE False END AS settlement_status,
                    (SELECT SUM(shagun_amount) FROM transaction_history WHERE receiver_uid = '{gift_data_obj.uid}') 
                    AS total_amount, u.name, bd.bank_name, bd.bank_logo, bd.account_number, u.profile_pic, pj.wish,
                    th.gifter_name
                FROM transaction_history AS th
                LEFT JOIN users As u ON th.sender_uid = u.uid
                LEFT JOIN event AS ev ON th.event_id = ev.id
                LEFT JOIN events_type AS et ON ev.event_type_id = et.id
                LEFT JOIN greeting_cards AS gc ON th.greeting_card_id = gc.id
                LEFT JOIN bank_details AS bd ON th.reciever_bank_id = bd.id
                LEFT JOIN print_jobs AS pj ON th.id = pj.transaction_id
                WHERE th.receiver_uid = '{gift_data_obj.uid}' 
                AND ( u.name LIKE '%{gift_data_obj.search}%' OR u.phone LIKE '%{gift_data_obj.search}%') 
                ORDER BY th.created_on DESC"""
            cursor.execute(sent_gift_query)
            received_gifts = cursor.fetchall()
            events_list = responseGenerator.generateResponse(events_data, EVENT_TYPE_LIST)
            total_gift_received, received_gift_list = responseGenerator.generateResponse(received_gifts, GIFT_SENT)

            return {
                "status": True,
                "events_list": events_list,
                "total_received_gifts": total_gift_received,
                "received_gifts": received_gift_list
            }, 200

    except pymysql.Error as e:
        return {"status": False, "message": str(e)}, 301
    except Exception as e:
        return {"status": False, "message": str(e)}, 301
