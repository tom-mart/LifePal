from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from typing import List
import os
import json
from pywebpush import webpush, WebPushException

from .models import PushSubscription
from .schemas import (
    PushSubscriptionSchema,
    PushSubscriptionResponseSchema,
    SendPushNotificationSchema,
    VAPIDPublicKeySchema,
    TestNotificationSchema
)

router = Router()


@router.get("/vapid-public-key", auth=JWTAuth(), response=VAPIDPublicKeySchema, tags=["Push Notifications"])
def get_vapid_public_key(request):
    """Get VAPID public key for push notification subscription"""
    public_key = os.environ.get('VAPID_PUBLIC_KEY', '')
    if not public_key:
        return 500, {"error": "VAPID keys not configured"}
    return {"public_key": public_key}


@router.post("/subscribe", auth=JWTAuth(), response={201: PushSubscriptionResponseSchema, 400: dict}, tags=["Push Notifications"])
def subscribe_to_push(request, payload: PushSubscriptionSchema):
    """Subscribe user to push notifications"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("🔔 PUSH NOTIFICATION SUBSCRIPTION REQUEST RECEIVED")
    logger.info("=" * 80)
    
    try:
        # Extract keys from the subscription
        p256dh = payload.keys.get('p256dh')
        auth = payload.keys.get('auth')
        
        logger.info(f"User: {request.user.username} (ID: {request.user.id})")
        logger.info(f"Endpoint: {payload.endpoint[:80]}...")
        logger.info(f"Keys present - p256dh: {bool(p256dh)}, auth: {bool(auth)}")
        logger.info(f"User agent: {payload.user_agent[:100] if payload.user_agent else 'Not provided'}")
        
        if not p256dh or not auth:
            logger.error("Missing required keys")
            return 400, {"error": "Missing required keys (p256dh, auth)"}
        
        # Create or update subscription
        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=payload.endpoint,
            defaults={
                'user': request.user,
                'p256dh_key': p256dh,
                'auth_key': auth,
                'user_agent': payload.user_agent,
                'is_active': True
            }
        )
        
        logger.info(f"Subscription {'created' if created else 'updated'} successfully")
        
        return 201, {
            'id': subscription.id,
            'endpoint': subscription.endpoint,
            'created_at': subscription.created_at,
            'is_active': subscription.is_active
        }
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}", exc_info=True)
        return 400, {"error": str(e)}


@router.delete("/unsubscribe", auth=JWTAuth(), response={200: dict, 404: dict}, tags=["Push Notifications"])
def unsubscribe_from_push(request, endpoint: str):
    """Unsubscribe from push notifications"""
    try:
        subscription = PushSubscription.objects.get(
            user=request.user,
            endpoint=endpoint
        )
        subscription.is_active = False
        subscription.save()
        return 200, {"success": True, "message": "Unsubscribed successfully"}
    except PushSubscription.DoesNotExist:
        return 404, {"error": "Subscription not found"}


@router.get("/subscriptions", auth=JWTAuth(), response=List[PushSubscriptionResponseSchema], tags=["Push Notifications"])
def get_user_subscriptions(request):
    """Get all active push subscriptions for the current user"""
    subscriptions = PushSubscription.objects.filter(
        user=request.user,
        is_active=True
    )
    return [
        {
            'id': sub.id,
            'endpoint': sub.endpoint,
            'created_at': sub.created_at,
            'is_active': sub.is_active
        }
        for sub in subscriptions
    ]


@router.post("/test", auth=JWTAuth(), response={200: dict, 400: dict, 500: dict}, tags=["Push Notifications"])
def send_test_notification(request, payload: TestNotificationSchema):
    """Send a test push notification to all user's devices"""
    try:
        vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY')
        vapid_claims = {
            "sub": os.environ.get('VAPID_SUBJECT', 'mailto:admin@lifepal.app')
        }
        
        if not vapid_private_key:
            return 500, {"error": "VAPID keys not configured on server"}
        
        subscriptions = PushSubscription.objects.filter(
            user=request.user,
            is_active=True
        )
        
        if not subscriptions.exists():
            return 400, {"error": "No active push subscriptions found"}
        
        success_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            try:
                notification_data = {
                    "title": "LifePal Test Notification",
                    "body": payload.message,
                    "icon": "/web-app-manifest-192x192.png",
                    "badge": "/favicon-96x96.png",
                    "tag": "test-notification",
                    "url": "/"
                }
                
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh_key,
                            "auth": subscription.auth_key
                        }
                    },
                    data=json.dumps(notification_data),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims
                )
                success_count += 1
                subscription.save()  # Update last_used timestamp
            except WebPushException as e:
                failed_count += 1
                if e.response and e.response.status_code in [404, 410]:
                    # Subscription is no longer valid
                    subscription.is_active = False
                    subscription.save()
        
        return 200, {
            "success": True,
            "message": f"Sent to {success_count} device(s), {failed_count} failed",
            "sent": success_count,
            "failed": failed_count
        }
    except Exception as e:
        return 500, {"error": str(e)}


def send_push_notification_to_user(user, title, body, icon=None, url=None, tag=None):
    """
    Helper function to send push notifications to a user.
    Can be called from other parts of the application.
    """
    try:
        vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY')
        vapid_claims = {
            "sub": os.environ.get('VAPID_SUBJECT', 'mailto:admin@lifepal.app')
        }
        
        if not vapid_private_key:
            return False
        
        subscriptions = PushSubscription.objects.filter(
            user=user,
            is_active=True
        )
        
        success = False
        for subscription in subscriptions:
            try:
                notification_data = {
                    "title": title,
                    "body": body,
                    "icon": icon or "/web-app-manifest-192x192.png",
                    "badge": "/favicon-96x96.png",
                    "tag": tag or "notification",
                    "url": url or "/"
                }
                
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh_key,
                            "auth": subscription.auth_key
                        }
                    },
                    data=json.dumps(notification_data),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims
                )
                success = True
                subscription.save()
            except WebPushException as e:
                if e.response and e.response.status_code in [404, 410]:
                    subscription.is_active = False
                    subscription.save()
        
        return success
    except Exception:
        return False
