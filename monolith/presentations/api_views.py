from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Presentation, Status
from events.models import Conference
from django.views.decorators.http import require_http_methods
import json, pika


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}

class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}





@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):

    if request.method == "GET":
        presentation = Presentation.objects.all()
        return JsonResponse(
            {"presentation": presentation},
            encoder=PresentationListEncoder
        )
    else:
        content = json.loads(request.body)
        status = "SUBMITTED"
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference"},
                status=400
            )
        presentation = Presentation.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_presentation(request, id):

    if request.method == "GET":
        presentation = Presentation.objects.filter(id=id)
        return JsonResponse(
            {"presentation": presentation},
            encoder=PresentationDetailEncoder
        )

    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)
        try:
            if "presentation" in content:
                presentation = Presentation.objects.get(id=content["presentation"])
                content["presentation"] = presentation
        except Presentation.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid presentation id"},
                status=400,
            )
    Presentation.objects.filter(id=id).update(**content)
    presentation = Presentation.objects.get(id=id)
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    channel.basic_publish(
        exchange="",
        routing_key="presentation_approvals",
        body=json.dumps({
            "presenter_name": presentation.presenter_name,
            "presenter_email": presentation.presenter_email,
            "title": presentation.title,
        }),
    )
    connection.close()
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='presentation_rejections')
    channel.basic_publish(
        exchange="",
        routing_key='presentation_rejections',
        body=json.dumps({
            "presenter_name": presentation.presenter_name,
            "presenter_email": presentation.presenter_email,
            "title": presentation.title,
        }),
    )
    connection.close()

    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False
    )

# @require_http_methods(["POST"])
# def api_submit_presentation(request, pk):
#     presentation = Presentation.objects.get(id=pk)
#     presentation.reject()
#     parameters = pika.ConnectionParameters(host="rabbitmq")
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()
#     channel.queue_declare(queue='presentation_submissions')
#     channel.basic_publish(
#         exchange="",
#         routing_key='presentation_submissions',
#         body=json.dumps({
#             "presenter_name": presentation.presenter_name,
#             "presenter_email": presentation.presenter_email,
#             "title": presentation.title,
#         }),
#     )
#     connection.close()

#     return JsonResponse(
#         presentation,
#         encoder=PresentationDetailEncoder,
#         safe=False
#     )


# def send_email(tasks, body):
#     parameters = pika.ConnectionParameters(host="rabbitmq")
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()
#     channel.queue_declare(queue=tasks)
#     channel.basic_publish(
#         exchange="",
#         routing_key=tasks,
#         body=json.dumps(body),
#     )
#     connection.close()
