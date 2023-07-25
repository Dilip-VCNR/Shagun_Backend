import json

from Shagun_backend.util.constants import *


class responseGenerator:
    @classmethod
    def generateResponse(cls, data, controller_type):
        if controller_type == CHECK_USER:
            return {
                "id": data[0],
                "name": data[2],
                "email": data[3],
                "phone": data[4],
                "Kyc": data[6],
                "profile": data[7],
                "user_id": data[1],
                "created_on": data[8]
            }

        if controller_type == EVENT_LIST:
            event_list = []
            for events in data:
                event_list.append(
                    {
                        "event_date": events[0],
                        "event_name": events[2],
                        "admins": json.loads(events[1]),
                        "event_id": events[3],
                        "is_approved": events[4],
                        "status": events[5],
                        "total_recieved_amount": events[6],
                        "total_senders_count": events[7]
                    }
                )
            return event_list

        if controller_type == ALL_EVENT_LIST:
            event_list = []
            for events in data:
                event_list.append(
                    {
                        "event_date": events[0],
                        "event_name": events[2],
                        "admins": json.loads(events[1]),
                        "event_id": events[3],
                        "is_approved": events[4],
                        "status": events[5]
                    }
                )
            return event_list

        if controller_type == SINGLE_EVENT:
            return {
                "event_date": data[0],
                "event_note": data[2],
                "address_line1": data[3],
                "address_line2": data[4],
                "event_lat_lng": data[5],
                "admins": json.loads(data[1]),
                "sub_events": json.loads(data[6])
            }

        if controller_type == EVENT_TYPE_LIST:
            event_type_list = []
            for event_type in data:
                event_type_list.append(
                    {
                        "id": event_type[0],
                        "event_type_name": event_type[1]
                    })
            return event_type_list

        if controller_type == EVENT_TYPE_BY_ID:
            return {
                "id": data[0],
                "event_type_name": data[1]
            }

        if controller_type == APP_COMPATIBILITY:
            return {
                "app_name": data[0],
                "min_version": data[1],
                "latest_version": data[2],
                "platform": data[3],
                "created": data[4],
                "updated": data[5],
            }

        if controller_type == USER_HOME_PAGE:
            total_recieved_amount = 0
            total_sent_amount = 0
            transaction_sent_list = []
            transaction_recieved_list = []
            events_invite_list = []
            for sent in data[0]:
                total_sent_amount = sent[5]
                transaction_sent_list.append(
                    {
                        "amount_sent": sent[0],
                        "event_name": sent[1],
                        "sent_to": sent[2],
                        "event_id": sent[3],
                        "profile_pic": sent[4]

                    }
                )

            for recieved in data[1]:
                total_recieved_amount = recieved[5]
                transaction_recieved_list.append(
                    {
                        "amount_received": recieved[0],
                        "even_name": recieved[1],
                        "received_from": recieved[2],
                        "event_id": recieved[3],
                        "profile_pic": recieved[4]
                    }
                )

            for invites in data[2]:
                events_invite_list.append(
                    {
                        "event_name": invites[0],
                        "event_date": invites[1],
                        "event_id": invites[3],
                        "is_gifted": invites[4],
                        "event_admins": json.loads(invites[2])
                    }
                )

            return total_sent_amount, transaction_sent_list, total_recieved_amount, transaction_recieved_list, \
                events_invite_list

        if controller_type == GIFT_SENT:
            sent_gift = []
            total_gift_amount = 0
            for sent in data:
                total_gift_amount = sent[11]
                sent_gift.append(
                    {
                        "receiver_uid": sent[0],
                        "sender_uid": sent[1],
                        "name": sent[12],
                        "shagun_amount": sent[2],
                        "transaction_amount": sent[3],
                        "transaction_fee": sent[4],
                        "delivery_fee": sent[5],
                        "created_on": sent[6],
                        "card_price": sent[7],
                        "event_type_name": sent[8],
                        "id": sent[9],
                        "settlement_status": sent[10],
                        "bank_name": sent[13],
                        "bank_logo": sent[14],
                        "acc_no": sent[15]
                    }
                )
            return total_gift_amount, sent_gift

        if controller_type == GREETING_CARDS:
            greeting_cards = []
            for cards in data:
                greeting_cards.append(
                    {
                        "card_name": cards[0],
                        "card_image_url": cards[1],
                        "card_price": cards[2],
                        "card_id": cards[3],
                        "card_status": cards[4]
                    }
                )
            return greeting_cards

        if controller_type == GREETING_CARDS_BY_ID:
            return {
                "id": data[0],
                "card_name": data[1]
            }

        if controller_type == TRACK_ORDER:
            track_order = []
            for order in data:
                track_order.append(
                    {
                        "shagun_amount": order[0],
                        "track_status": order[1],
                        "is_gift_card_sent": order[2],
                        "shagun_gifted_on": order[3]
                    }
                )
            return track_order

        if controller_type == ALL_EVENT_TYPE_LIST:
            event_type_lists = []
            for event_type in data:
                event_type_lists.append(
                    {
                        "event_type_id": event_type[0],
                        "event_type_name": event_type[1],
                        "status": event_type[2]
                    }
                )
            return event_type_lists

        if controller_type == ALL_LOCATION_LIST:
            location_lists = []
            for event_type in data:
                location_lists.append(
                    {
                        "location_id": event_type[0],
                        "location_name": event_type[1],
                        "status": event_type[2]
                    }
                )
            return location_lists

        if controller_type == LOCATION_BY_ID:
            return {
                "id": data[0],
                "city_name": data[1]
            }

        if controller_type == ALL_KYC_DATA:
            kyc_data = []
            for kyc in data:
                kyc_data.append(
                    {
                        "id": kyc[0],
                        "uid": kyc[1],
                        "full_name": kyc[2],
                        "dob": kyc[3],
                        "permanent_address": kyc[4],
                        "identification_proof1": kyc[5],
                        "identification_proof2": kyc[6],
                        "identification_number1": kyc[7],
                        "identification_number2": kyc[8],
                        "identification_doc1": kyc[9],
                        "identification_doc2": kyc[10],
                        "verification_status": kyc[11],
                        "profile_pic": kyc[12]

                    }
                )
            return kyc_data

        if controller_type == ALL_BANK_DATA:
            bank_data = []
            for bank in data:
                bank_data.append(
                    {
                        "id": bank[0],
                        "uid": bank[1],
                        "ifsc_code": bank[2],
                        "bank_name": bank[3],
                        "account_holder_name": bank[4],
                        "account_number": bank[5],
                        "status": bank[6],
                        "profile_pic": bank[7]

                    }
                )
            return bank_data

        if controller_type == ALL_USERS_DATA:
            user_data = []
            for user in data:
                user_data.append(
                    {
                        "id": user[0],
                        "uid": user[1],
                        "name": user[2],
                        "email": user[3],
                        "phone": user[4],
                        "auth_type": user[5],
                        "kyc": user[6],
                        "profile_pic": user[7],
                        "created_on": user[8],
                        "status": user[9]

                    }
                )
            return user_data

        if controller_type == ALL_PRINTERS_DATA:
            printer_data = []
            for printer in data:
                printer_data.append(
                    {
                        "id": printer[0],
                        "store_name": printer[1],
                        "city": printer[2],
                        "address": printer[3],
                        "status": printer[4],
                        "gst_no": printer[5],
                        "store_owner": printer[6],
                        "contact_number": printer[7]
                    }

                )
            return printer_data

        if controller_type == INVITED_EVENT_LIST:
            events_invite_list = []
            for invites in data:
                events_invite_list.append(
                    {
                        "event_name": invites[0],
                        "event_date": invites[1],
                        "event_id": invites[3],
                        "is_gifted": invites[4],
                        "event_admins": json.loads(invites[2])
                    }
                )
            return events_invite_list

        if controller_type == GET_BANK_DATA:
            bank_data = []
            for bank in data:
                bank_data.append(
                    {
                        "bank_name": bank[0],
                        "acc_no": bank[1],
                        "ifsc_code": bank[2],
                        "status": bank[3]
                    }

                )
            return bank_data

        if controller_type == GET_KYC_DATA:
            return {
                data[0][0]: data[0][2],
                data[0][1]: data[0][3],
                "status": data[0][4]
            }

        if controller_type == BANK_LISTS:
            bank_lists = []
            for bank in data:
                bank_lists.append(
                    {
                        "bank_id": bank[0],
                        "bank_name": bank[1],
                        "bank_logo": bank[2],
                        "bank_status": bank[3]
                    }

                )
            return bank_lists

        if controller_type == ACTIVE_LOCATIONS_LIST:
            locations_lists = []
            for bank in data:
                locations_lists.append(
                    {
                        "city_id": bank[0],
                        "city_name": bank[1]
                    }

                )
            return locations_lists


