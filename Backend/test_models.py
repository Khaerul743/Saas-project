#!/usr/bin/env python3
"""
Test script to verify that all models can be imported and relationships work correctly
"""

try:
    # Import all models in the correct order
    from app.models.company_information.company_entity import CompanyInformation
    from app.models.document.document_entity import Document
    from app.models.history_message.history_entity import HistoryMessage
    from app.models.history_message.metadata_entity import Metadata
    from app.models.integration.integration_entity import Integration
    from app.models.platform.platform_entity import Platform
    from app.models.user.api_key_entity import ApiKey
    from app.models.user.user_entity import User
    from app.models.user_agent.user_agent_entity import UserAgent
    from app.models.agent.agent_entity import Agent
    
    print("✅ All models imported successfully!")
    
    # Test database connection and query
    from app.configs.database import SessionLocal
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
