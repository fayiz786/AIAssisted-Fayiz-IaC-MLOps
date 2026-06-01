import time
import logging
import statistics
import random
from dataclasses import dataclass, field
from typing import Optional
import json
from datetime import datetime, timezone

# ANSI escape codes for colors
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("model_monitor")

ENDPOINT_URL = "[your-model-endpoint.example.com](https://your-model-endpoint.example.com/predict)"
LATENCY_SLA_MS = 300          # Alert if p95 latency exceeds this
DRIFT_PSI_THRESHOLD = 0.2     # PSI > 0.2 = significant drift
POLL_INTERVAL_SECONDS = 10
N_REQUESTS_PER_POLL = 5


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Alert:
    alert_type: str          # "LATENCY" | "DRIFT"
    severity: str            # "WARNING" | "CRITICAL"
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class MonitoringResult:
    latency_ms_samples: list[float]
    p95_latency_ms: float
    psi_score: float
    alerts: list[Alert]
    endpoint_healthy: bool


# ---------------------------------------------------------------------------
# Simulated endpoint call (replace with real requests.post in production)
# ---------------------------------------------------------------------------

def call_endpoint(payload: dict) -> tuple[float, Optional[dict]]:
    """
    Calls the model endpoint and returns (latency_ms, response).
    Simulates real HTTP call — swap this block with:

        import requests
        start = time.perf_counter()
        resp = requests.post(ENDPOINT_URL, json=payload, timeout=5)
        latency = (time.perf_counter() - start) * 1000
        return latency, resp.json()
    """
    start = time.perf_counter()

    # Simulate variable latency (occasionally spikes to trigger alerts)
    simulated_latency = random.gauss(mu=180, sigma=60)
    time.sleep(max(simulated_latency / 1000, 0))

    latency_ms = (time.perf_counter() - start) * 1000

    # Simulated response
    response = {
        "prediction": random.choice([0, 1]),
        "confidence": round(random.uniform(0.5, 0.99), 4),
    }
    return latency_ms, response


# ---------------------------------------------------------------------------
# PSI drift detection
# ---------------------------------------------------------------------------

def compute_psi(baseline: list[float], current: list[float], bins: int = 10) -> float:
    """
    Population Stability Index — compares current feature distribution
    against a baseline. PSI < 0.1: stable, 0.1–0.2: moderate shift,
    > 0.2: significant drift.
    """
    min_val = min(min(baseline), min(current))
    max_val = max(max(baseline), max(current))
    bin_edges = [min_val + (max_val - min_val) * i / bins for i in range(bins + 1)]

    def to_dist(data):
        counts = [0] * bins
        for val in data:
            for i in range(bins):
                if bin_edges[i] <= val < bin_edges[i + 1]:
                    counts[i] += 1
                    break
            else:
                counts[-1] += 1  # catch max edge
        total = len(data)
        # Smooth to avoid log(0)
        return [max(c / total, 1e-6) for c in counts]

    base_dist = to_dist(baseline)
    curr_dist = to_dist(current)

    import math
    psi = sum(
        (c - b) * math.log(c / b)
        for b, c in zip(base_dist, curr_dist)
    )
    return round(psi, 4)


# ---------------------------------------------------------------------------
# Monitoring core
# ---------------------------------------------------------------------------

def check_latency(latency_samples: list[float]) -> Optional[Alert]:
    sorted_samples = sorted(latency_samples)
    p95_idx = int(len(sorted_samples) * 0.95)
    p95 = sorted_samples[min(p95_idx, len(sorted_samples) - 1)]

    if p95 > LATENCY_SLA_MS * 1.5:
        return Alert(
            alert_type="LATENCY",
            severity="CRITICAL",
            message=f"p95 latency {p95:.1f}ms exceeds 1.5× SLA ({LATENCY_SLA_MS}ms)",
            metadata={"p95_ms": p95, "sla_ms": LATENCY_SLA_MS},
        )
    elif p95 > LATENCY_SLA_MS:
        return Alert(
            alert_type="LATENCY",
            severity="WARNING",
            message=f"p95 latency {p95:.1f}ms exceeds SLA ({LATENCY_SLA_MS}ms)",
            metadata={"p95_ms": p95, "sla_ms": LATENCY_SLA_MS},
        )
    return None


def check_drift(psi: float, feature_name: str = "confidence") -> Optional[Alert]:
    if psi > DRIFT_PSI_THRESHOLD:
        severity = "CRITICAL" if psi > 0.25 else "WARNING"
        return Alert(
            alert_type="DRIFT",
            severity=severity,
            message=f"Feature '{feature_name}' PSI={psi} exceeds threshold {DRIFT_PSI_THRESHOLD}",
            metadata={"psi": psi, "feature": feature_name},
        )
    return None


def run_monitoring_cycle(baseline_confidences: list[float]) -> MonitoringResult:
    """Execute one monitoring poll: collect latency + drift, raise alerts."""
    latency_samples = []
    current_confidences = []

    for _ in range(N_REQUESTS_PER_POLL):
        payload = {"feature_1": round(random.uniform(0, 1), 3),
                   "feature_2": round(random.uniform(0, 1), 3)}
        latency, response = call_endpoint(payload)
        latency_samples.append(latency)
        if response:
            current_confidences.append(response["confidence"])

    p95 = sorted(latency_samples)[int(len(latency_samples) * 0.95)]
    psi = compute_psi(baseline_confidences, current_confidences)

    alerts = []
    latency_alert = check_latency(latency_samples)
    drift_alert = check_drift(psi)
    if latency_alert:
        alerts.append(latency_alert)
    if drift_alert:
        alerts.append(drift_alert)

    return MonitoringResult(
        latency_ms_samples=latency_samples,
        p95_latency_ms=p95,
        psi_score=psi,
        alerts=alerts,
        endpoint_healthy=len(alerts) == 0,
    )


def emit_alerts(result: MonitoringResult) -> None:
    """Log results — replace with PagerDuty / Slack / CloudWatch Logs hook."""
    status = "✅ HEALTHY" if result.endpoint_healthy else "🚨 DEGRADED"
    logger.info(
        f"{status} | p95={result.p95_latency_ms:.1f}ms | PSI={result.psi_score}"
    )
    for alert in result.alerts:
        if alert.severity == "CRITICAL":
            log_fn = logger.critical
            color_code = RED
        elif alert.severity == "WARNING":
            log_fn = logger.warning
            color_code = YELLOW
        else:
            log_fn = logger.info
            color_code = ""
        log_fn(f"{color_code}[{alert.alert_type}] {alert.severity}: {alert.message}{RESET}")
        # Structured log for ingestion by CloudWatch / Datadog
        print(json.dumps({
            "event": "model_alert",
            **vars(alert)
        }))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting MLOps model monitor...")
    logger.info(f"Endpoint: {ENDPOINT_URL}")
    logger.info(f"Latency SLA: {LATENCY_SLA_MS}ms | Drift PSI threshold: {DRIFT_PSI_THRESHOLD}")

    # Baseline: historical confidence scores from your model registry / feature store
    # In production, load from S3: s3://mlops-model-artifacts-prod/baselines/confidence.json
    baseline_confidences = [round(random.gauss(0.75, 0.08), 4) for _ in range(200)]

    cycle = 0
    while True:
        cycle += 1
        logger.info(f"--- Poll cycle #{cycle} ---")
        try:
            result = run_monitoring_cycle(baseline_confidences)
            emit_alerts(result)
        except Exception as exc:
            logger.error(f"Monitor cycle failed: {exc}", exc_info=True)

        time.sleep(POLL_INTERVAL_SECONDS)