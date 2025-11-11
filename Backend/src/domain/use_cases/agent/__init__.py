"""
Agent use cases module.
"""

from .calculate_agent_stats_use_case import (
    CalculateAgentStatsUseCase,
    CalculateStatsInput,
    CalculateStatsOutput,
)
from .create_agent_entity import (
    CreateAgentEntity,
    CreateAgentEntityInput,
    CreateAgentEntityOutput,
)
from .delete_agent_use_case import (
    DeleteAgentInput,
    DeleteAgentOutput,
    DeleteAgentUseCase,
)
from .document import (
    AddDocumentToAgent,
    AddDocumentToAgentInput,
    UploadedDocumentHandler,
    UploadedDocumentInput,
)
from .format_agent_data_use_case import (
    FormatAgentDataInput,
    FormatAgentDataOutput,
    FormatAgentDataUseCase,
)
from .get_agents_with_details_use_case import (
    GetAgentsWithDetailsInput,
    GetAgentsWithDetailsOutput,
    GetAgentsWithDetailsUseCase,
)
from .get_all_agents_use_case import (
    GetAllAgentsInput,
    GetAllAgentsOutput,
    GetAllAgentsUseCase,
)
from .get_user_agents_use_case import (
    GetUserAgentsInput,
    GetUserAgentsOutput,
    GetUserAgentsUseCase,
)
from .history_message import (
    CreateHistoryMessage,
    CreateHistoryMessageInput,
    CreateMetadata,
    CreateMetadataInput,
)
from .initial_agent_again import InitialAgentAgain, InitialAgentAgainInput
from .integration import (
    ApiIntegration,
    ApiIntegrationInput,
    CreateIntegration,
    CreateIntegrationInput,
    GenerateApiKey,
    GenerateApiKeyInput,
    SendTelegramUserMessage,
    SendTelegramUserMessageInput,
    TelegramIntegration,
    TelegramIntegrationInput,
)
from .invoke import (
    InvokeAgent,
    InvokeAgentApi,
    InvokeAgentApiInput,
    InvokeAgentInput,
    InvokeAgentOutput,
)
from .simple_rag import (
    CreateSimpleRagAgent,
    CreateSimpleRagAgentInput,
    InitialSimpleRagAgent,
    InitialSimpleRagAgentInput,
)
from .store_agent_in_memory import StoreAgentInMemory, StoreAgentInMemoryInput
from .store_agent_obj import StoreAgentObj, StoreAgentObjInput
from .user_agent import CreateUserAgent, CreateUserAgentInput

__all__ = [
    "AddDocumentToAgent",
    "AddDocumentToAgentInput",
    "FormatAgentDataUseCase",
    "FormatAgentDataInput",
    "FormatAgentDataOutput",
    "CalculateAgentStatsUseCase",
    "CalculateStatsInput",
    "CalculateStatsOutput",
    "GetUserAgentsUseCase",
    "GetUserAgentsInput",
    "GetUserAgentsOutput",
    "GetAgentsWithDetailsUseCase",
    "GetAgentsWithDetailsInput",
    "GetAgentsWithDetailsOutput",
    "DeleteAgentUseCase",
    "DeleteAgentInput",
    "DeleteAgentOutput",
    "GetAllAgentsUseCase",
    "GetAllAgentsInput",
    "GetAllAgentsOutput",
    "UploadedDocumentHandler",
    "UploadedDocumentInput",
    "GetUserAgentsInput",
    "GetUserAgentsOutput",
    "GetUserAgentsUseCase",
    "CreateAgentEntity",
    "CreateAgentEntityInput",
    "CreateAgentEntityOutput",
    "CreateSimpleRagAgent",
    "CreateSimpleRagAgentInput",
    "StoreAgentObjInput",
    "StoreAgentObj",
    "CreateUserAgent",
    "CreateUserAgentInput",
    "CreateHistoryMessage",
    "CreateHistoryMessageInput",
    "CreateMetadata",
    "CreateMetadataInput",
    "StoreAgentInMemory",
    "StoreAgentInMemoryInput",
    "InitialSimpleRagAgent",
    "InitialSimpleRagAgentInput",
    "InvokeAgent",
    "InvokeAgentInput",
    "InvokeAgentOutput",
    "InitialAgentAgain",
    "InitialAgentAgainInput",
    "ApiIntegration",
    "ApiIntegrationInput",
    "CreateIntegration",
    "CreateIntegrationInput",
    "GenerateApiKey",
    "GenerateApiKeyInput",
    "InvokeAgentApi",
    "InvokeAgentApiInput",
    "TelegramIntegration",
    "TelegramIntegrationInput",
    "SendTelegramUserMessageInput",
    "SendTelegramUserMessage",
]
