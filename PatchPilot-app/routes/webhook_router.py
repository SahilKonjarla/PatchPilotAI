import logging

from fastapi import APIRouter, Request

from service.webhook_service import github_webhook

logger = logging.getLogger(__name__)
webhook_router = APIRouter()

@webhook_router.post("/webhook")
async def webhook(request: Request):
    logger.info("Received GitHub webhook request")
    response = await github_webhook(request)
    return response
