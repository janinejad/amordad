# import logging
#
# import requests
# import json
# from farapayamak import soap, Rest_Client
#
# from j_settings.models import SMSSetting
#
#
# def payamak_khadamati_send_sms(moblil, params, bodyId):
#     sms_setting = SMSSetting.objects.all().first()
#     if sms_setting.api_type == "MELIPAYAMAR":
#         NEW_URL = 'https://console.melipayamak.com/api/send/shared/62227e0b5f4945088267470ac8293089'
#         NEW_HEADERS = {'Content-type': 'application/json; utf-8', 'Accept': 'application/json'}
#         newBody = {
#             "bodyId": bodyId,
#             "to": moblil,
#             "args": params
#         }
#         response = requests.post(NEW_URL, data=json.dumps(newBody), headers=NEW_HEADERS)
#     elif sms_setting.api_type == "RAZPAYAMAK":
#         restClient = Rest_Client(sms_setting.username, sms_setting.password)
#         # Soap_Client = soap.Soap_Client(sms_setting.username, sms_setting.password)
#         # response = Soap_Client.SendByBaseNumber(params, moblil, bodyId)
#         param_text = ";".join(params)
#         response = restClient.BaseServiceNumber(param_text, moblil, bodyId)
#
