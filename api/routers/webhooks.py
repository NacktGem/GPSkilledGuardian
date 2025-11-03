"""Payment webhook router for FastAPI."""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from bot.database import get_db_session
from bot.models import Payment, PaymentStatus, WebhookLog, User
from bot.utils import logger
from config import settings
import hashlib
import hmac

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature.
    
    Args:
        payload: Webhook payload
        signature: Provided signature
        secret: Webhook secret
        
    Returns:
        True if valid, False otherwise
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@router.post("/payment")
async def payment_webhook(request: Request):
    """Handle payment webhook notifications.
    
    Args:
        request: FastAPI request
        
    Returns:
        Success response
    """
    try:
        payload = await request.json()
        
        # Log webhook
        async with get_db_session() as session:
            log = WebhookLog(
                webhook_type="payment",
                payload=str(payload),
                status="received"
            )
            session.add(log)
            await session.commit()
        
        logger.info(f"Received payment webhook: {payload}")
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"Error processing payment webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/blockcypher")
async def blockcypher_webhook(
    request: Request,
    x_eventtype: Optional[str] = Header(None),
    x_eventid: Optional[str] = Header(None)
):
    """Handle BlockCypher webhook for crypto payments.
    
    Args:
        request: FastAPI request
        x_eventtype: BlockCypher event type header
        x_eventid: BlockCypher event ID header
        
    Returns:
        Success response
    """
    try:
        payload = await request.json()
        
        # Log webhook
        async with get_db_session() as session:
            log = WebhookLog(
                webhook_type="blockcypher",
                payload=str(payload),
                status="received"
            )
            session.add(log)
            await session.flush()
            
            # Process transaction confirmation
            if x_eventtype == "tx-confirmation":
                tx_hash = payload.get("hash")
                confirmations = payload.get("confirmations", 0)
                
                # Find payment by transaction hash
                result = await session.execute(
                    select(Payment).where(Payment.transaction_id == tx_hash)
                )
                payment = result.scalar_one_or_none()
                
                if payment:
                    payment.confirmations = confirmations
                    
                    if confirmations >= settings.payment_confirmation_blocks:
                        payment.status = PaymentStatus.COMPLETED
                        payment.completed_at = datetime.utcnow()
                        
                        # Update user
                        result = await session.execute(
                            select(User).where(User.discord_id == payment.user_id)
                        )
                        user = result.scalar_one_or_none()
                        if user:
                            user.total_payments += 1
                            user.total_spent_usd += payment.amount_usd
                            user.last_payment_at = datetime.utcnow()
                        
                        logger.info(f"Payment {payment.id} completed")
                    else:
                        payment.status = PaymentStatus.CONFIRMING
                        logger.info(f"Payment {payment.id} confirming: {confirmations}/{settings.payment_confirmation_blocks}")
                    
                    log.status = "processed"
                    log.processed_at = datetime.utcnow()
            
            await session.commit()
        
        logger.info(f"Processed BlockCypher webhook: {x_eventtype}")
        
        return {"status": "processed"}
    
    except Exception as e:
        logger.error(f"Error processing BlockCypher webhook: {e}")
        
        # Update log with error
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(WebhookLog).order_by(WebhookLog.id.desc()).limit(1)
                )
                log = result.scalar_one_or_none()
                if log:
                    log.status = "failed"
                    log.error_message = str(e)
                    await session.commit()
        except:
            pass
        
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
