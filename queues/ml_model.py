import os

from django.conf import settings
from django.utils import timezone

MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_waiting_model.joblib')

FEATURES = ['ahead', 'avg_service_time', 'counters', 'hour', 'weekday']


def build_dataset():
    from .models import QueueEntry

    rows = []
    targets = []
    entries = QueueEntry.objects.filter(
        status='COMPLETED',
        waiting_time_minutes__isnull=False,
    ).select_related('service', 'service__department')

    for e in entries:
        rows.append([
            max((e.position or 1) - 1, 0),
            e.service.average_service_time_minutes or 10,
            e.counters_at_join or 1,
            e.join_time.hour,
            e.join_time.weekday(),
        ])
        targets.append(e.waiting_time_minutes)

    return rows, targets


def simulate_history(n=600, seed=42):
    """Generates simulated historical data for model evaluation."""
    import random

    rng = random.Random(seed)
    rows = []
    targets = []

    for _ in range(n):
        avg_service = float(rng.choice([5, 10, 15, 30]))
        counters = rng.randint(1, 3)
        ahead = rng.randint(0, 30)
        hour = rng.randint(8, 16)
        weekday = rng.randint(0, 4)

        # Simulating human fatigue and peak hour slowdowns
        fatigue = 1.0 + 0.02 * ahead
        peak = 1.25 if 10 <= hour <= 12 else 1.0
        noise = rng.gauss(0, avg_service * 0.2)

        wait = (ahead * avg_service * fatigue * peak) / counters + noise
        rows.append([ahead, avg_service, counters, hour, weekday])
        targets.append(max(0.0, wait))

    return rows, targets


def load_model():
    try:
        import joblib
    except ImportError:
        return None

    if not os.path.exists(MODEL_PATH):
        return None

    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def predict_waiting_time(service, ahead):
    model = load_model()
    if model is None:
        return None

    try:
        features = [[
            max(ahead, 0),
            service.average_service_time_minutes or 10,
            service.department.counters.filter(active=True).count() or 1,
            timezone.now().hour,
            timezone.now().weekday(),
        ]]
        value = model.predict(features)[0]
        return max(0, int(round(value)))
    except Exception:
        return None