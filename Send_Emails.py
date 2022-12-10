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
    number= "+447759500535"
    account_sid = "AC8ca18366c8cd6c7afc4a740fe596cbfc"
    auth_token = "5d606694a69b87390fb5b878ce96484a"
    client = Client(account_sid,auth_token)
    message = client.messages.create(
							  from_= "+16506403506",
							  body = msg,
							  to = number
                        )

    return (OTP)