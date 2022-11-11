from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Conference, Location, State
from django.views.decorators.http import require_http_methods
from .acls import get_photo, get_weather_data
import json


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
        "description",
        "temp",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
        # "temp",
    ]
    encoders = {
        "location": LocationListEncoder(),
        # "temp": LocationDetailEncoder(),
    }


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]


@require_http_methods(["GET", "POST"])
def api_list_conferences(request):

    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder
        )
    else:
        content = json.loads(request.body)
        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400
            )
        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, id):
    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        state = conference.location.state
        city = conference.location.city
        weather = get_weather_data(city, state)
        return JsonResponse(
            {
            "conference": conference,
            "weather": weather,
            },
            encoder=ConferenceDetailEncoder
        )

    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conference = Conference.objects.get(id=content["conference"])
                content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )
    Conference.objects.filter(id=id).update(**content)
    conference = Conference.objects.get(id=id)
    return JsonResponse(
        conference,
        encoder=ConferenceDetailEncoder,
        safe=False,
    )


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder
        )

    else:
        content = json.loads(request.body)
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
            photo = get_photo(content["city"], content["state"].abbreviation)
            content.update(photo)
            description = get_weather_data(content["city"], content["state"])
            temp = get_weather_data(content["city"], content["state"])
            content.update(description)
            content.update(temp)
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400
            )
        location = Location.objects.create(**content)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    if request.method == "GET":
        locations = Location.objects.filter(id=id)
        return JsonResponse(
            locations,
            encoder=LocationDetailEncoder,
            safe=False
        )

    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
    Location.objects.filter(id=id).update(**content)
    location = Location.objects.get(id=id)
    return JsonResponse(
        location,
        encoder=LocationDetailEncoder,
        safe=False,
    )
