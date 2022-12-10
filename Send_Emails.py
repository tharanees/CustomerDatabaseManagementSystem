import smtplib, ssl
import random
import os
from twilio.rest import Client

def Send_email():
    def generateOTP():
        return (random.randrange(100000, 999999))
    OTP = generateOTP()
    otp = "YOUR OTP IS "+str(OTP)
    msg = (otp + ".\n" +"This is an auto-generated sms.\n"+"Sincerely Sivaguru Hardware Team.")
    number= "REPLACE WITH ADMIN'S PHONE NUMBER TO WHICH OTP WILL BE SENT"
    account_sid = "FILL IN TWILIO ACCOUNT SID"
    auth_token = "FILL IN TWILIO ACCOUNT AUTH_TOKEN"
    client = Client(account_sid,auth_token)
    message = client.messages.create(
							  from_= "FILL IN TWILIO ACCOUNT PHONE NUMBER",
							  body = msg,
							  to = number
                        )

    return (OTP)
