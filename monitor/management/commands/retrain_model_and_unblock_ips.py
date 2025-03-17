import os
import pandas as pd
import lightgbm as lgb
from django.core.management.base import BaseCommand
from django.utils import timezone
from monitor.models import BlockedIP, AutomationHistory
import joblib

class Command(BaseCommand):
    help = 'Retrains ML model and unblocks expired IPs'

    def handle(self, *args, **kwargs):
        self.stdout.write("🔄 Starting ML model retraining and IP unblock process...")

        # ✅ 1. Retrain LightGBM Model
        try:
            dataset_path = os.path.join('ml_engine', 'supervised_request_logs.csv')
            data = pd.read_csv(dataset_path)
            X = data[['request_count', 'avg_interval', 'method_code', 'path_depth']]
            y = data['label']

            model = lgb.LGBMClassifier(
                objective='binary',
                boosting_type='gbdt',
                learning_rate=0.1,
                num_leaves=31,
                n_estimators=100,
                random_state=42
            )
            model.fit(X, y)

            joblib.dump(model, os.path.join('ml_engine', 'lightgbm_model.pkl'))
            self.stdout.write(self.style.SUCCESS("✅ LightGBM model retrained and saved successfully."))

            AutomationHistory.objects.create(
                task_name="ML Model Retraining",
                status="Success",
                message="LightGBM model retrained and saved."
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during model retraining: {e}"))
            AutomationHistory.objects.create(
                task_name="ML Model Retraining",
                status="Failed",
                message=str(e)
            )

        # ✅ 2. Auto-Unblock Expired IPs
        try:
            now = timezone.now()
            expired_ips = BlockedIP.objects.filter(is_permanent=False, unblock_at__lt=now)
            count = expired_ips.count()
            expired_ips.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ {count} expired IP(s) unblocked successfully."))

            AutomationHistory.objects.create(
                task_name="Auto-Unblock IPs",
                status="Success",
                message=f"Unblocked {count} expired IP(s)."
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during IP unblock: {e}"))
            AutomationHistory.objects.create(
                task_name="Auto-Unblock IPs",
                status="Failed",
                message=str(e)
            )
