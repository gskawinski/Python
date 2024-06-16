import json
import os
import smtplib
from email.mime.text import MIMEText
import requests
from email.message import EmailMessage
from confluent_kafka import Consumer, KafkaError, KafkaException


# function to send email
def send_email(subject, body, sender, recipients, password):
    # Create a MIMEText object with the body of the email.
    msg = MIMEText(body)
    # Set the subject of the email.
    msg["Subject"] = subject
    # Set the sender's email.
    msg["From"] = sender
    # Join the list of recipients into a single string separated by commas.
    msg["To"] = ", ".join(recipients)

    # Connect to Gmail's SMTP server using SSL.
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        # Login to the SMTP server using the sender's credentials.
        smtp_server.login(sender, password)
        # Send the email. The sendmail function requires the sender's email, the list of recipients, and the email message as a string.
        smtp_server.sendmail(sender, recipients, msg.as_string())
    # Print a message to console after successfully sending the email.
    print("Message sent!")


# topic
ORDER_CONFIRMED_KAFKA_TOPIC = "food_order_confirmed"

print(f"Kafka Consumer config => Topic: {ORDER_CONFIRMED_KAFKA_TOPIC}")

# Parse Consumer configuration.
conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "main",
    "session.timeout.ms": 6000,
    "auto.offset.reset": "earliest",
}
# Create Consumer instance
c = Consumer(conf)
# Subscribe to topic
c.subscribe([ORDER_CONFIRMED_KAFKA_TOPIC])

print(f"Kafka Consumer [{ORDER_CONFIRMED_KAFKA_TOPIC}] start listening")

# set of sent emails
emails_sent_set = set()

# Poll for new messages from Kafka and proces them.
try:
    while True:
        msg = c.poll(timeout=1.0)

        if msg is None:
            # print("Waiting...")
            continue
        if msg.error():
            print(f"ERROR: {msg.error()}".format(msg.error()))
            raise KafkaException(msg.error())
        else:
            print(
                f"{msg.topic()} [{msg.partition()}] at offset {msg.offset()} with key {str(msg.key())}:\n"
            )
            # get message data
            topic_recived = msg.topic()
            part_ = msg.partition()
            offset = msg.offset()
            key = msg.key()
            value = msg.value().decode("utf-8")
            # print(f"Consumed event from topic {topic_recived}: key = {key} value = {value}")
            consumed_message = json.loads(msg.value().decode("utf-8"))
            # print(consumed_message)

            food_order_email = consumed_message["user_email"]
            print(f"Sending email to {food_order_email} ")

            # Create and send email
            # Define the subject and body of the email.
            subject = "Your Food Order"
            body = "Your oder details"
            # Define the sender's email address.
            sender = "sender@gmail.com"
            EMAIL_ADDRESS = "sender@gmail.com"
            # List of recipients to whom the email will be sent.
            recipients = ["recipient1@gmail.com", "recipient2@gmail.com"]
            # Password for the sender's email account.
            password = "password"  # APP PASSWORD for GMAIL
            EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

            # Call the function to send the email.
            # send_email(subject, body, sender, recipients, password)

            # update sent email db (set)
            emails_sent_set.add(food_order_email)
            print(f"Total unique emails sent: {len(emails_sent_set)}\n")

except Exception as e:
    import traceback

    print(traceback.format_exc())
except KeyboardInterrupt:
    pass
finally:
    # Leave group and commit final offsets
    c.close()
