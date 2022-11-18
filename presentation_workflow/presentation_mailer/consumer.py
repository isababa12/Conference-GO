import json, pika, django, os, sys, time
from django.core.mail import send_mail
from pika.exceptions import AMQPConnectionError

sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval(ch, method, properties, body):
    data = json.loads(body)
    email = data["presenter_email"]
    name = data["presenter_name"]
    title = data["title"]
    send_mail(
        "Subject: Your presentation has been accepted",
        f"{name}, we're happy to tell you that your presentation {title} has been accepted.",
        "admin@conference.go",
        [email],
        fail_silently=False,
    )


def process_rejection(ch, method, properties, body):
    data = json.loads(body)
    email = data["presenter_email"]
    name = data["presenter_name"]
    title = data["title"]
    send_mail(
        "Subject: Your presentation has been rejected",
        f"{name}, unfortunately your presentation {title} has been rejected.",
        "admin@conference.go",
        [email],
        fail_silently=False,
    )


# def process_submission(ch, method, properties, body):
#     data = json.loads(body)
#     email = data["presenter_email"]
#     name = data["presenter_name"]
#     title = data["title"]
#     send_mail(
#         "Subject: Your presentation has been submitted",
#         f"{name}, your presentation {title} has been submitted.",
#         "admin@conference.go",
#         [email],
#         fail_silently=False,
#     )


while True:
    try:
        parameters = pika.ConnectionParameters(host='rabbitmq')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='presentation_approvals')
        channel.queue_declare(queue='presentation_rejections')
        # channel.queue_declare(queue='presentation_submissions')
        channel.basic_consume(
            queue='presentation_approvals',
            on_message_callback=process_approval,
            auto_ack=True,
        )
        channel.basic_consume(
            queue='presentation_rejections',
            on_message_callback=process_rejection,
            auto_ack=True,
        )
        # channel.basic_consume(
        #     queue='presentation_submissions',
        #     on_message_callback=process_submission,
        #     auto_ack=True,
        # )
        channel.start_consuming()
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)
