import pytest

from app.schemas.chat import ChatRequest, ChecklistRequest


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(message="How do I apply for a visa?")
        assert req.message == "How do I apply for a visa?"
        assert req.session_id is None
        assert req.nationality is None

    def test_request_with_context(self):
        req = ChatRequest(
            message="Can I work on a student visa?",
            nationality="Indian",
            current_visa="Stamp 2",
        )
        assert req.nationality == "Indian"
        assert req.current_visa == "Stamp 2"

    def test_empty_message_fails(self):
        with pytest.raises(ValueError):
            ChatRequest(message="")

    def test_message_too_long_fails(self):
        with pytest.raises(ValueError):
            ChatRequest(message="x" * 2001)


class TestChecklistRequest:
    def test_valid_request(self):
        req = ChecklistRequest(
            goal="Apply for Critical Skills Employment Permit",
            nationality="Indian",
            current_status="Student Stamp 2",
        )
        assert req.goal == "Apply for Critical Skills Employment Permit"
        assert req.nationality == "Indian"