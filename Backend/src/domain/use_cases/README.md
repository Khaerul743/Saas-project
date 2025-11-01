# Use Cases Architecture

## Overview

This module implements the **Use Case Pattern** for business logic, providing a clean separation between business rules and infrastructure concerns.

## Architecture Benefits

### ✅ **Separation of Concerns**
- **Use Cases**: Pure business logic, no infrastructure dependencies
- **Repository**: Data access only
- **Service**: Orchestration and error handling
- **Controller**: HTTP request/response handling

### ✅ **Testability**
- Use cases can be tested independently
- Easy to mock dependencies
- Business logic is isolated from infrastructure

### ✅ **Reusability**
- Use cases can be reused across different services
- Business logic is not tied to specific API endpoints

### ✅ **Maintainability**
- Clear boundaries between layers
- Easy to modify business rules without affecting infrastructure

## Structure

```
src/domain/use_cases/
├── base/                           # Base classes and interfaces
│   ├── base_use_case.py           # Abstract base use case
│   └── use_case_result.py         # Result wrapper pattern
├── interfaces/                     # Repository interfaces
│   └── agent_repository_interface.py
├── agent/                         # Agent-specific use cases
│   ├── format_agent_data_use_case.py
│   ├── calculate_agent_stats_use_case.py
│   ├── get_user_agents_use_case.py
│   ├── get_agents_with_details_use_case.py
│   ├── delete_agent_use_case.py
│   └── get_all_agents_use_case.py
└── README.md                      # This file
```

## Usage Examples

### 1. Simple Use Case
```python
# Create use case instance
format_use_case = FormatAgentDataUseCase()

# Execute with input
result = await format_use_case.execute(
    FormatAgentDataInput(agents=agent_list)
)

# Handle result
if result.is_success():
    formatted_data = result.data.formatted_agents
else:
    error_message = result.get_error()
```

### 2. Orchestrated Use Case
```python
# Use case that coordinates multiple other use cases
get_user_agents_use_case = GetUserAgentsUseCase(
    agent_repository=agent_repo,
    format_agent_data_use_case=format_use_case,
    calculate_stats_use_case=stats_use_case
)

# Execute
result = await get_user_agents_use_case.execute(
    GetUserAgentsInput(user_id=123)
)
```

### 3. Service Integration
```python
class AgentService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.agent_repo = AgentRepository(db)
        
        # Initialize use cases
        self.get_user_agents_use_case = GetUserAgentsUseCase(
            self.agent_repo,
            FormatAgentDataUseCase(),
            CalculateAgentStatsUseCase()
        )
    
    async def get_user_agents_with_statistics(self, user_id: int) -> dict:
        result = await self.get_user_agents_use_case.execute(
            GetUserAgentsInput(user_id=user_id)
        )
        
        if result.is_error():
            raise Exception(result.get_error())
        
        return {
            "user_agents": result.data.user_agents,
            "stats": result.data.stats
        }
```

## Testing Use Cases

### Unit Test Example
```python
import pytest
from unittest.mock import Mock, AsyncMock

from src.domain.use_cases.agent import FormatAgentDataUseCase, FormatAgentDataInput

@pytest.mark.asyncio
async def test_format_agent_data_use_case():
    # Arrange
    use_case = FormatAgentDataUseCase()
    mock_agents = [
        Mock(id="1", name="Test Agent", model="gpt-4o", role="assistant")
    ]
    input_data = FormatAgentDataInput(agents=mock_agents)
    
    # Act
    result = await use_case.execute(input_data)
    
    # Assert
    assert result.is_success()
    assert len(result.data.formatted_agents) == 1
    assert result.data.formatted_agents[0]["name"] == "Test Agent"
```

## Best Practices

### 1. **Single Responsibility**
Each use case should handle one specific business operation.

### 2. **Input Validation**
Always validate input data in the `validate_input` method.

### 3. **Error Handling**
Use `UseCaseResult` to handle success and error states consistently.

### 4. **Dependency Injection**
Pass dependencies through constructor, not through method parameters.

### 5. **Async/Await**
All use cases should be async to support database operations.

### 6. **Type Hints**
Use proper type hints for better IDE support and documentation.

## Migration from Service Layer

### Before (Service Layer)
```python
class AgentService:
    async def get_user_agents_with_statistics(self, user_id: int):
        # Business logic mixed with infrastructure
        agents = await self.agent_repo.get_user_agents_with_integrations(user_id)
        
        # Complex formatting logic
        formatted_agents = []
        for agent in agents:
            # ... complex formatting logic ...
        
        # Statistics calculation
        stats = self._calculate_agent_statistics(agents)
        
        return {"user_agents": formatted_agents, "stats": stats}
```

### After (Use Case Pattern)
```python
class AgentService:
    def __init__(self, db: AsyncSession, request=None):
        self.get_user_agents_use_case = GetUserAgentsUseCase(
            self.agent_repo,
            FormatAgentDataUseCase(),
            CalculateAgentStatsUseCase()
        )
    
    async def get_user_agents_with_statistics(self, user_id: int):
        # Clean orchestration
        result = await self.get_user_agents_use_case.execute(
            GetUserAgentsInput(user_id=user_id)
        )
        
        if result.is_error():
            raise Exception(result.get_error())
        
        return {
            "user_agents": result.data.user_agents,
            "stats": result.data.stats
        }
```

## Future Enhancements

1. **Event Sourcing**: Add domain events to use cases
2. **CQRS**: Separate command and query use cases
3. **Saga Pattern**: For complex multi-step operations
4. **Caching**: Add caching layer to use cases
5. **Metrics**: Add performance monitoring to use cases
