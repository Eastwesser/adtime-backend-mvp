from uuid import UUID
from typing import Dict, List
import hmac
import hashlib

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logger.logger import logger

class WebhookValidator:
    """Validate webhook signatures and payloads"""
    
    @staticmethod
    def validate_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Validate webhook signature using HMAC-SHA256"""
        if not signature or not secret:
            logger.warning("Missing signature or secret for webhook validation")
            return False
            
        expected_signature = hmac.new(
            secret.encode(), 
            payload, 
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def validate_order_webhook(payload: Dict) -> List[str]:
        """Validate order webhook payload structure"""
        errors = []
        required_fields = ['order_id', 'status', 'timestamp', 'event_type']
        
        for field in required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")
                
        # Validate status values
        if 'status' in payload and payload['status'] not in ['created', 'paid', 'processing', 'completed', 'cancelled']:
            errors.append(f"Invalid status value: {payload['status']}")
            
        # Validate timestamp format
        if 'timestamp' in payload:
            try:
                timestamp = float(payload['timestamp'])
                if timestamp <= 0:
                    errors.append("Timestamp must be positive")
            except (ValueError, TypeError):
                errors.append("Timestamp must be numeric")
                
        # Validate order_id format (UUID) - ADD THIS VALIDATION
        if 'order_id' in payload:
            try:
                UUID(payload['order_id'])
            except (ValueError, TypeError):
                errors.append("order_id must be a valid UUID")
                
        return errors

# Global instance
webhook_validator = WebhookValidator()
