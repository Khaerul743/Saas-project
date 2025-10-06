from app.configs.database import SessionLocal
from app.models.integration.integration_entity import Integration
from app.services.telegram import set_webhook
from app.models.platform.platform_entity import Platform
from app.utils.agent_utils import generate_api_key

def add_integration(agent_id: str, platform: str, status: str):
    with SessionLocal() as db:
        new_integration = Integration(
            agent_id=agent_id, platform=platform, status=status
        )
        db.add(new_integration)
        db.commit()
        db.refresh(new_integration)
        return new_integration

async def platform_integration(agent_id: str, user_id: int, integration_id: int, platform_type: str, api_key: str):
    with SessionLocal() as db:
        try:
            if platform_type == "telegram":
                # Ensure webhook is set successfully BEFORE creating Platform record
                webhook = await set_webhook(api_key, integration_id)
                if not webhook.get("status"):
                    return {
                        "status": False,
                        "response": webhook.get("response"),
                    }

                platform_integration = Platform(
                    integration_id=integration_id,
                    platform_type=platform_type,
                    api_key=api_key,
                )
                db.add(platform_integration)
                db.commit()
                db.refresh(platform_integration)

            elif platform_type == "api":
                # Generate API key, then create Platform record and commit
                generated_api_key = generate_api_key(db, user_id, agent_id)
                platform_integration = Platform(
                    integration_id=integration_id,
                    platform_type=platform_type,
                    api_key=generated_api_key,
                )
                db.add(platform_integration)
                db.commit()
                db.refresh(platform_integration)

            return {
                "status": True,
                "response": "Integration added successfully",
            }
        except Exception as e:
            # Rollback on any error to avoid partial writes
            try:
                db.rollback()
            except Exception:
                pass
            return {
                "status": False,
                "response": f"Error adding integration: {e}",
            }