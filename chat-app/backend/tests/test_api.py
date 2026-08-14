import json
import unittest
import warnings
from unittest.mock import patch
import os

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables import RunnableLambda

from app.main import app
from app.config import get_settings
from app.models import ModelDefinition


warnings.filterwarnings("ignore", category=DeprecationWarning)


async def fake_model_stream(_prompt):
    yield AIMessageChunk(content="Hello ")
    yield AIMessageChunk(
        content="world",
        usage_metadata={
            "input_tokens": 4,
            "output_tokens": 2,
            "total_tokens": 6,
        },
        response_metadata={"finish_reason": "stop"},
    )


FAKE_DEFINITION = ModelDefinition(
    id="gemini-flash",
    provider="gemini",
    display_name="Gemini Flash",
    model_name="test-model",
    api_key="test-key",
)


def parse_sse(body: str) -> list[tuple[str, dict]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = block.splitlines()
        event = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        events.append((event, data))
    return events


class ApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_catalog_endpoints(self) -> None:
        models = self.client.get("/models")
        templates = self.client.get("/templates")

        self.assertEqual(models.status_code, 200)
        self.assertEqual({item["id"] for item in models.json()}, {
            "gemini-flash",
            "groq-llama",
            "mistral-small",
        })
        self.assertEqual(templates.status_code, 200)
        self.assertEqual(templates.json()[0]["id"], "explain-concept")

    def test_configured_frontend_origin_is_allowed(self) -> None:
        response = self.client.options(
            "/models",
            headers={
                "Origin": "http://localhost:4200",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "http://localhost:4200",
        )

    def test_cors_origins_are_read_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {"CORS_ALLOWED_ORIGINS": "https://one.example, https://two.example"},
        ):
            get_settings.cache_clear()
            self.assertEqual(
                get_settings().cors_allowed_origins,
                ["https://one.example", "https://two.example"],
            )
        get_settings.cache_clear()

    def test_unknown_model_is_rejected_before_streaming(self) -> None:
        response = self.client.post(
            "/chat/stream",
            json={"model_id": "unknown", "message": "Hello"},
        )
        self.assertEqual(response.status_code, 404)

    def test_template_inputs_are_validated_before_streaming(self) -> None:
        response = self.client.post(
            "/templates/explain-concept/stream",
            json={"model_id": "gemini-flash", "inputs": {}},
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("topic", response.json()["detail"])

    @patch("app.routes.chat.create_chat_model")
    def test_general_chat_stream_contract(self, create_model) -> None:
        create_model.return_value = (FAKE_DEFINITION, RunnableLambda(fake_model_stream))

        response = self.client.post(
            "/chat/stream",
            json={"model_id": "gemini-flash", "message": "Say hello"},
        )
        events = parse_sse(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([name for name, _ in events], ["start", "token", "token", "done"])
        self.assertEqual("".join(data["text"] for name, data in events if name == "token"), "Hello world")
        details = events[-1][1]["details"]
        self.assertEqual(details["total_tokens"], 6)
        self.assertEqual(details["finish_reason"], "stop")
        self.assertEqual(details["chunk_count"], 2)

    @patch("app.routes.chat.create_chat_model")
    def test_template_chat_stream_contract(self, create_model) -> None:
        create_model.return_value = (FAKE_DEFINITION, RunnableLambda(fake_model_stream))

        response = self.client.post(
            "/templates/explain-concept/stream",
            json={
                "model_id": "gemini-flash",
                "inputs": {"topic": "prompt templates"},
            },
        )
        events = parse_sse(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(events[0][1]["mode"], "template")
        self.assertEqual(events[-1][0], "done")


if __name__ == "__main__":
    unittest.main()
