from ninja import Router, Schema
from django.http import JsonResponse
from notifications.models import Device

router = Router(tags=["notifications"])

class DeviceTokenSchema(Schema):
    token: str

@router.post("/device/register")
def register_device(request, payload: DeviceTokenSchema):
    token = payload.token

    if not token:
        return JsonResponse({"error": "Token is required"}, status=400)

    # Remove any old devices with the same token
    Device.objects.filter(token=token).delete()

    # Create a new device for the authenticated user
    Device.objects.create(user=request.user, token=token)
    return JsonResponse({"success": "Device registered successfully"})