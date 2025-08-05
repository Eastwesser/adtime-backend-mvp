from http.client import HTTPException
from time import time
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

# Unified metric definitions
PAYMENT_METRICS = {
    'amounts': Histogram(
        "payment_amounts_rub",
        "Payment amounts distribution",
        buckets=[100, 500, 1000, 5000]
    ),
    'errors': Counter(
        'payment_errors_total',
        'Payment processing errors',
        ['type']
    ),
    'status_changes': Counter(
        'payment_status_total',
        'Payment status changes',
        ['status']
    )
}

ORDER_METRICS = {
    'transitions': Counter(
        'order_status_transitions_total',
        'Order status transitions',
        ['from', 'to']
    )
}

# Other non-duplicate metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP Request Latency",
    ["method", "endpoint"]
)

GENERATION_TIME = Histogram(
    "generation_processing_seconds",
    "Time spent processing generations",
    ["model_version"]
)

def setup_monitoring(app):
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(
            content=generate_latest(REGISTRY),
            media_type="text/plain"
        )

    @app.get("/health")
    async def health_check():
        try:
            generate_latest(REGISTRY)
            return {"status": "healthy", "metrics": "available"}
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))

    @app.middleware("http")
    async def monitor_requests(request: Request, call_next):
        start_time = time()
        method = request.method
        endpoint = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
            PAYMENT_METRICS['status_changes'].labels(status='success').inc()
        except Exception as e:
            status_code = 500
            PAYMENT_METRICS['status_changes'].labels(status='error').inc()
            PAYMENT_METRICS['errors'].labels(type=type(e).__name__).inc()
            raise
        finally:
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint
            ).observe(time() - start_time)

        return response
    