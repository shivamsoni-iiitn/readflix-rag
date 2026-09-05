import boto3
import logfire
from app.config import settings
import asyncio


client = boto3.client(
    "bedrock-runtime",
    region_name=settings.AWS_REGION,
)


async def check(text: str, source: str = "INPUT"):
    with logfire.span("aws_guardrail", source=source):
        response = await asyncio.to_thread(
            client.apply_guardrail,
            guardrailIdentifier=settings.AWS_GUARDRAIL_ID,
            guardrailVersion=settings.AWS_GUARDRAIL_VERSION,
            source=source,
            content=[
                {
                    "text": {
                        "text": text
                    }
                }
            ],
        )
        action=response['action']

        logfire.info("AWS Guardrail result", action=action,source=source,)
        if action == "GUARDRAIL_INTERVENED":
            message = response.get("outputs", [{}])[0].get(
                "text",
                "I can help with Readflix Library questions.",
            )

            return {
                "action": "blocked",
                "message": message,
            }

        return {
            "action": "allow",
            "message": None,
        }
