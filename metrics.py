from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask import request
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

def setup_metrics(app):
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        request_latency = time.time() - request.start_time
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=request.path, 
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method, 
            endpoint=request.path
        ).observe(request_latency)
        return response

    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
