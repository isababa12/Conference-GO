from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from common.json import ModelEncoder
from .models import Attendee
from events.models import Conference
from events.api_views import ConferenceListEncoder
import json


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]

    encoders = {
        "conference": ConferenceListEncoder(),
    }

@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    """
    Lists the attendees names and the link to the attendee
    for the specified conference id.

    Returns a dictionary with a single key "attendees" which
    is a list of attendee names and URLS. Each entry in the list
    is a dictionary that contains the name of the attendee and
    the link to the attendee's information.

    {
        "attendees": [
            {
                "name": attendee's name,
                "href": URL to the attendee,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
        )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )
        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, id):
    """
    Returns the details for the Attendee model specified
    by the id parameter.

    This should return a dictionary with email, name,
    company name, created, and conference properties for
    the specified Attendee instance.

    {
        "email": the attendee's email,
        "name": the attendee's name,
        "company_name": the attendee's company's name,
        "created": the date/time when the record was created,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """

    # attendees = Attendee.objects.get(id=id)

    # return JsonResponse(
    #     {
    #         "email": attendees.email,
    #         "name": attendees.name,
    #         "company_name": attendees.company_name,
    #         "created": attendees.created,
    #         "conference": {
    #             "name": attendees.conference.name,
    #             "href": attendees.conference.get_api_url(),
    #     }
    # })
    if request.method == "GET":
        attendee = Attendee.objects.filter(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )

    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)
        try:
            if "attendee" in content:
                attendee = Attendee.objects.get(id=content["attendee"])
                content["attendee"] = attendee
        except Attendee.DoesNotExist:
            return JsonResponse(
                {"message": "Attendee does not exist"},
                status=400,
            )
    Attendee.objects.filter(id=id).update(**content)
    attendee = Attendee.objects.get(id=id)
    return JsonResponse(
        attendee,
        encoder=AttendeeDetailEncoder,
        safe=False,
    )
