#!/usr/bin/env python3
"""
Test script to verify that all models can be imported and relationships work correctly
"""

try:
    # Import all models in the correct order
    from src.domain.models.company_entity import CompanyInformation
    from src.domain.models.document_entity import Document
    from src.domain.models.history_entity import HistoryMessage
    from src.domain.models.metadata_entity import Metadata
    from src.domain.models.integration_entity import Integration
    from src.domain.models.platform_entity import Platform
    from src.domain.models.api_key_entity import ApiKey
    from src.domain.models.user_entity import User
    from src.domain.models.user_agent_entity import UserAgent
    from src.domain.models.agent_entity import Agent

    print("✅ All models imported successfully!")

    # Test database connection and query
    from src.config.database import SessionLocal
    from app.utils.agent_utils import generate_agent_id

    db = SessionLocal()
    try:
        # Test the generate_agent_id function
        agent_id = generate_agent_id(db)
        print(f"✅ Generated agent ID: {agent_id}")

        # Test a simple query
        agents = db.query(Agent).limit(1).all()
        print(f"✅ Database query successful! Found {len(agents)} agents")

    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        db.close()

except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback

    traceback.print_exc()
