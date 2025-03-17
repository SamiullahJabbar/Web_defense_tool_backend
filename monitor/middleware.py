import datetime
import joblib
import numpy as np
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog, Website, BlockedIP
from django.core.mail import send_mail

# Load LightGBM model
model = joblib.load("ml_engine/lightgbm_model.pkl")

class MLDetectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = request.META.get('REMOTE_ADDR')
        path = request.path
        method = request.method
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # 🔍 Identify website based on the request domain
        host = request.get_host().split(':')[0]  # Extract domain without port
        website = Website.objects.filter(domain=host).first()  # Find website by domain

        if not website:
            return  # Skip processing if no website found

        user = website.user  # ✅ Define user properly

        # 🔐 Check if IP is already blocked for this user's website
        blocked = BlockedIP.objects.filter(ip_address=ip, website=website).first()
        if blocked:
            if blocked.is_permanent or (blocked.unblock_at and timezone.now() < blocked.unblock_at):
                return HttpResponseForbidden("🚫 Access Denied. Your IP has been blocked.")

        # 🛠 Fix LightGBM Input Issue
        feature_names = ["request_count", "avg_interval", "method_code", "path_depth"]
        request_count = 50
        avg_interval = 2.5
        method_code = 0 if method == 'GET' else 1
        path_depth = path.count('/')
        input_data = np.array([[request_count, avg_interval, method_code, path_depth]])

        # ✅ Convert input to dictionary with feature names
        input_data_dict = {name: value for name, value in zip(feature_names, input_data[0])}

        # 🧠 ML Prediction
        prediction_prob = model.predict_proba([list(input_data_dict.values())])[0][1]
        is_anomalous = True if prediction_prob >= 0.5 else False

        # ✅ Save RequestLog with user
        RequestLog.objects.create(
            user=user,  # Save user
            website=website,
            ip_address=ip,
            path=path,
            method=method,
            user_agent=user_agent,
            anomaly_score=round(prediction_prob, 4),
            is_anomalous=is_anomalous,
            timestamp=timezone.now()
        )

        # 🚫 Auto-block logic for specific website
        if is_anomalous and prediction_prob > 0.8:
            BlockedIP.objects.get_or_create(
                ip_address=ip,
                website=website,  # Block per website
                defaults={
                    "block_reason": "ML detected suspicious activity",
                    "is_permanent": False,
                    "unblock_at": timezone.now() + datetime.timedelta(minutes=10)
                }
            )

            # 📧 Email Alert to website owner
            if hasattr(website, 'email') and website.email:
                try:
                    send_mail(
                        subject='🚨 Web Defense Alert: Suspicious Activity Detected',
                        message=f'An attack was detected from IP {ip} at {path} on your website. ML score: {round(prediction_prob, 4)}.',
                        from_email=None,
                        recipient_list=[website.email],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Email send error: {e}")
