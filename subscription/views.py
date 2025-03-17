from django.utils import timezone
from datetime import timedelta
from .utils import is_paid_user
import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import Subscription
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from monitor.models import Website
from monitor.models import RequestLog,BlockedIP

def has_free_scan_limit_exceeded(ip):
    today = timezone.now().date()
    scan_count = RequestLog.objects.filter(
        ip_address=ip,
        timestamp__date=today,
    ).count()
    return scan_count >= 20



from rest_framework.views import APIView
from rest_framework.response import Response
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Subscription
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateStripeCheckoutSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Create a Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Pro Plan - Website Monitoring Subscription',
                            },
                            'unit_amount': 1400,  # $4.00
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url='http://localhost:3000/subscription-success?session_id={CHECKOUT_SESSION_ID}',  # Frontend URL
                cancel_url='http://localhost:3000/subscription-cancelled',  # Frontend URL
                metadata={
                    'user_id': request.user.id  # Store the user ID in metadata
                }
            )

            # Return the checkout URL to the frontend
            return Response({"checkout_url": checkout_session.url})

        except Exception as e:
            # Log the error and return a meaningful response
            print(f"Error creating Stripe checkout session: {str(e)}")
            return Response({"error": "Failed to create checkout session. Please try again."}, status=400)

class VerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            session_id = request.data.get('session_id')
            if not session_id:
                return Response({"error": "Session ID is required"}, status=400)

            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            # Check if the payment was successful
            if session.payment_status == 'paid':
                # Update the user's subscription in the database
                user_id = session.metadata.get('user_id')
                if not user_id:
                    return Response({"error": "User ID not found in session metadata"}, status=400)

                # Update or create the subscription
                Subscription.objects.update_or_create(
                    user_id=user_id,
                    defaults={
                        'plan_name': 'Pro',
                        'is_active': True,
                        'expires_on': timezone.now() + timezone.timedelta(days=30)  # 1-month subscription
                    }
                )

                return Response({"success": True})
            else:
                return Response({"error": "Payment not completed"}, status=400)

        except Exception as e:
            # Log the error and return a meaningful response
            print(f"Error verifying payment: {str(e)}")
            return Response({"error": "Failed to verify payment. Please contact support."}, status=400)



@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']

            Subscription.objects.update_or_create(
                user_id=user_id,
                defaults={
                    'plan_name': 'Pro',
                    'is_active': True,
                    'expires_on': timezone.now() + timezone.timedelta(days=30)
                }
            )

        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(status=400)




class SubscriptionStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        subscription = Subscription.objects.filter(user=user, is_active=True).first()

        if subscription and (not subscription.expires_on or subscription.expires_on > timezone.now()):
            return Response({
                "plan": subscription.plan_name,
                "status": "Active",
                "expires_on": subscription.expires_on,
                "subscribed_on": subscription.subscribed_on
            })
        else:
            return Response({
                "plan": "Free",
                "status": "Inactive",
                "expires_on": None,
                "subscribed_on": None
            })


class WebsiteLinkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # ✅ Ensure User Has a Pro Plan Subscription
        subscription = Subscription.objects.filter(user=user, is_active=True).first()
        if not subscription or subscription.plan_name != 'Pro' or (
            subscription.expires_on and subscription.expires_on <= timezone.now()
        ):
            return Response({"error": "Only Pro Plan users can link websites."}, status=403)

        # ✅ Ensure Each User Can Only Link ONE Website
        if Website.objects.filter(user=user).exists():
            return Response({"error": "You can only link one website."}, status=400)

        # ✅ Validate Input Fields
        url = request.data.get("url")
        domain = request.data.get("domain")
        ip_address = request.data.get("ip_address")
        email = request.data.get("email")

        if not all([url, domain, ip_address, email]):
            return Response({"error": "Missing required fields."}, status=400)

        # ✅ Create New Website
        Website.objects.create(user=user, url=url, domain=domain, ip_address=ip_address, email=email)

        return Response({"message": "✅ Website successfully linked to your account."}, status=201)

    def get(self, request):
        user = request.user
        websites = Website.objects.filter(user=user)  # ✅ Only User's Own Websites

        website_data = [
            {
                "id": website.id,
                "url": website.url,
                "domain": website.domain,
                "ip_address": website.ip_address,
                "email": website.email,
            }
            for website in websites
        ]
        return Response({"websites": website_data})

    def put(self, request):
        user = request.user
        website = get_object_or_404(Website, user=user)  # ✅ Securely Fetch User's Website

        # ✅ Update Fields If Provided
        website.url = request.data.get("url", website.url)
        website.domain = request.data.get("domain", website.domain)
        website.ip_address = request.data.get("ip_address", website.ip_address)
        website.email = request.data.get("email", website.email)

        website.save()
        return Response({"message": "✅ Website details updated successfully."})

    def delete(self, request):
        user = request.user
        website = get_object_or_404(Website, user=user)  # ✅ Ensure User Owns Website

        website.delete()
        return Response({"message": "✅ Website deleted successfully."})

class ScanUsageLogsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  
        today = timezone.now().date()
        website = Website.objects.filter(user=user).first()
        if not website:
            return Response({"error": "No linked website found for this user."}, status=404)

        logs = RequestLog.objects.filter(website=website, timestamp__date=today)  

        total_scans = logs.count()
        anomalies_detected = logs.filter(is_anomalous=True).count()

        return Response({
            "date": str(today),
            "user": user.username,
            "website": website.url,  
            "total_scans_today": total_scans,
            "anomalies_detected": anomalies_detected
        })



class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user 
        today = timezone.now().date()

        website = Website.objects.filter(user=user).first()
        if not website:
            return Response({"error": "No linked website found for this user."}, status=404)
        total_requests = RequestLog.objects.filter(website=website).count()
        total_anomalies = RequestLog.objects.filter(website=website, is_anomalous=True).count()
        total_blocked_ips = BlockedIP.objects.filter(website=website).count()
        today_scans = RequestLog.objects.filter(website=website, timestamp__date=today).count()

        return Response({
            "user": user.username,
            "website": website.url, 
            "total_requests": total_requests,
            "total_anomalies": total_anomalies,
            "total_blocked_ips": total_blocked_ips,
            "today_scans": today_scans
        })

class StripeSuccessRedirectView(View):
    def get(self, request):
        session_id = request.GET.get('session_id')

        # Optional: You can use session_id to fetch session from Stripe if needed
        # session = stripe.checkout.Session.retrieve(session_id)

        # Redirect to frontend dashboard after success
        return redirect('/dashboard')  # replace with your frontend dashboard URL path
