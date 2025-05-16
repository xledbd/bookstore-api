import json
import logging
import sys
import time
from flask import request, g

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": time.time(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        # Add request information if available
        if hasattr(g, 'request_id'):
            log_record["request_id"] = g.request_id
        
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
            
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    
    return logger

def log_request_middleware(app):
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = request.headers.get('X-Request-ID', '')
        
        app.logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.user_agent.string
            }
        )
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        
        app.logger.info(
            f"Request completed: {request.method} {request.path} {response.status_code}",
            extra={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration": duration
            }
        )
        
        return response
