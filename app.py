import json
import boto3
import ast
import sys
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def lambda_handler(event, context):
    # TODO implement
    session = boto3.Session()
    client = session.client('elbv2')
    s3 = session.client('s3')
    print("EVENT: ",event)
    file_object = event["Records"][0]
    event_username = file_object["userIdentity"]["principalId"]
    username = event_username[event_username.find(':',4)+1:]
    filename = file_object["s3"]["object"]["key"]
    action_time = file_object["eventTime"]
    print(filename)
    
    def send_email(final_text):
        from_email = "satishkumar.venu@tavant.com"
        to_email = "satishkumar.venu@tavant.com"   
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Fairway Broker Maintainance Page Notification !!!!!"
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Create the body of the message (a plain-text and an HTML version).
        text = final_text
        html = """\
        <html>
          <head></head>
          <body>
            <h2> 
            Hi,<br>
            {final_text}<br>
            please verify.<br>
            </h2>
          </body>
        </html>
        """.format(final_text=final_text)
        
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        
        # Send the message via local SMTP server.
        s = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com','587')
        s.starttls()
        s.login('AKIAVJ7T5QESJST2ICUE','BJdgMOrLrkX2ykYPdSkJjrendQ0yOe5Yi6/088wU8jIM')
        s.sendmail(from_email, to_email, msg.as_string())
        s.quit()


    if filename=='invoke.txt':
        email_text="Maintainance page has been invoked by user : {} at {}".format(event_username,action_time)
        response = client.modify_listener(ListenerArn='arn:aws:elasticloadbalancing:us-east-1:050812479762:listener/app/fwb-dev-app-alb/a1ddeb440aaf0861/2a83ea20ed1c429d',DefaultActions=[ { 'Type': 'forward','TargetGroupArn':'arn:aws:elasticloadbalancing:us-east-1:050812479762:targetgroup/maint-page-tg/221bb45efb64caa7'}])
        s3.copy_object(Bucket='fwb-dev-maintpage-test-dest',CopySource='/fwb-dev-maintpage-test/invoke.txt',Key='invoke.txt')
        s3.delete_object(Bucket='fwb-dev-maintpage-test',Key='invoke.txt')
        send_email(email_text)
    elif filename=='revoke.txt':
        response = client.modify_listener(ListenerArn='arn:aws:elasticloadbalancing:us-east-1:050812479762:listener/app/fwb-dev-app-alb/a1ddeb440aaf0861/2a83ea20ed1c429d',DefaultActions=[ { 'Type': 'forward','TargetGroupArn':'arn:aws:elasticloadbalancing:us-east-1:050812479762:targetgroup/fwb-dev-app-alb-tg/26042d4f27adb995'}])
        email_text="Maintainance page has been revoked by user : {} at {}".format(event_username,action_time)
        s3.copy_object(Bucket='fwb-dev-maintpage-test-dest',CopySource='/fwb-dev-maintpage-test/revoke.txt',Key='revoke.txt')
        s3.delete_object(Bucket='fwb-dev-maintpage-test',Key='revoke.txt')
        send_email(email_text)
        
