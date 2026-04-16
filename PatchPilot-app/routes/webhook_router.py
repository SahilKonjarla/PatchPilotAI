from fastapi import APIRouter, Request

from service.webhook_service import github_webhook

webhook_router = APIRouter()

@webhook_router.post("/webhook")
async def webhook(request: Request):
    response = await github_webhook(request)
    return response
