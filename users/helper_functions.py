from django.http import JsonResponse


def negative_response() -> JsonResponse:
    return JsonResponse({
        'message': '-1'
    })
