import pytest
from fastapi import UploadFile
from io import BytesIO
from types import SimpleNamespace
import asyncio

from src.domain.use_cases.agent.document.uploaded_document import (
    UploadedDocumentHandler,
    UploadedDocumentInput,
    UploadedDocumentOutput,
)
from src.domain.use_cases.base.use_case_result import UseCaseResult

# A dummy UploadFile
class DummyUploadFile:
    def __init__(self, filename="test.txt", content_type="text/plain", data=b"data"):
        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(data)

@pytest.fixture
def mock_save_file_handler(mocker):
    handler = mocker.Mock()
    handler.convert_to_hex = mocker.AsyncMock(return_value="deadbeef")
    handler.create_agent_directory = mocker.Mock(return_value="/tmp/agent/dir")
    handler.save_uploaded_file = mocker.Mock(return_value=None)
    return handler

@pytest.fixture
def mock_doc_repo(mocker):
    repo = mocker.Mock()
    # The object returned here should have .id, .file_name, .content_type
    repo.add_document = mocker.AsyncMock(return_value=SimpleNamespace(
        id=123, file_name="test.txt", content_type="text/plain"
    ))
    return repo

@pytest.mark.asyncio
async def test_uploaded_document_success(mock_save_file_handler, mock_doc_repo):
    handler = UploadedDocumentHandler(mock_doc_repo, mock_save_file_handler)
    dummy_file = DummyUploadFile()
    input_data = UploadedDocumentInput(
        user_id=1,
        agent_id="agentA",
        file=dummy_file,
    )
    result = await handler.execute(input_data)
    assert result.is_success()
    output = result.get_data()
    assert isinstance(output, UploadedDocumentOutput)
    assert output.document_id == 123
    assert output.file_name == "test.txt"
    assert output.content_type == "text/plain"
    assert output.agent_id == "agentA"

@pytest.mark.asyncio
async def test_uploaded_document_file_too_large(mock_save_file_handler, mock_doc_repo):
    handler = UploadedDocumentHandler(mock_doc_repo, mock_save_file_handler)
    # Make convert_to_hex raise ValueError
    mock_save_file_handler.convert_to_hex.side_effect = ValueError("Too large")
    dummy_file = DummyUploadFile()
    input_data = UploadedDocumentInput(
        user_id=2,
        agent_id="agentB",
        file=dummy_file,
    )
    result = await handler.execute(input_data)
    assert result.is_error()
    assert "File too large" in result.get_error()

@pytest.mark.asyncio
async def test_uploaded_document_unexpected_error(mock_save_file_handler, mock_doc_repo):
    handler = UploadedDocumentHandler(mock_doc_repo, mock_save_file_handler)
    # Make create_agent_directory raise Exception
    mock_save_file_handler.convert_to_hex.side_effect = None
    mock_save_file_handler.create_agent_directory.side_effect = Exception("Disk error")
    dummy_file = DummyUploadFile()
    input_data = UploadedDocumentInput(
        user_id=3,
        agent_id="agentC",
        file=dummy_file,
    )
    result = await handler.execute(input_data)
    assert result.is_error()
    assert "Unexpected error" in result.get_error()