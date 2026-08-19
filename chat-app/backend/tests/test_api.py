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
from app.review_schemas import ReviewAnalysis


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
        configured_origin = get_settings().cors_allowed_origins[0]
        response = self.client.options(
            "/models",
            headers={
                "Origin": configured_origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            configured_origin,
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
        self.assertEqual(details["response_content"], "Hello world")

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

    @patch("app.routes.reviews.analyze_review")
    def test_review_analysis_stream_returns_each_model_result(self, analyze) -> None:
        async def result_for(model_id, _review, strategy):
            return {
                "model_id": model_id,
                "provider": model_id.split("-")[0],
                "model_name": "test-model",
                "strategy": strategy,
                "analysis": ReviewAnalysis(
                    sentiment="negative",
                    rating=2,
                    summary="Good delivery but poor battery life.",
                    pros=["fast delivery"],
                    cons=["short battery life"],
                    recommendation=False,
                ).model_dump(),
                "details": {"total_tokens": 25},
            }

        analyze.side_effect = result_for
        response = self.client.post(
            "/reviews/analyze/stream",
            json={
                "review": "Fast delivery, but the battery lasts only two hours.",
                "model_ids": ["gemini-flash", "groq-llama", "mistral-small"],
                "strategy": "native",
            },
        )
        events = parse_sse(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(events[0][0], "start")
        self.assertEqual(
            sum(name == "model_result" for name, _ in events),
            3,
        )
        self.assertEqual(events[-1][0], "done")
        self.assertEqual(events[-1][1]["successful"], 3)
        self.assertEqual(events[-1][1]["failed"], 0)

    @patch("app.routes.reviews.analyze_review")
    def test_review_analysis_keeps_other_results_when_one_model_fails(self, analyze) -> None:
        async def result_for(model_id, _review, strategy):
            if model_id == "mistral-small":
                raise ValueError("Invalid structured response")
            return {
                "model_id": model_id,
                "provider": "test",
                "model_name": "test-model",
                "strategy": strategy,
                "analysis": ReviewAnalysis(
                    sentiment="neutral",
                    rating=3,
                    summary="Mixed review.",
                    pros=[],
                    cons=[],
                    recommendation=False,
                ).model_dump(),
                "details": {},
            }

        analyze.side_effect = result_for
        response = self.client.post(
            "/reviews/analyze/stream",
            json={
                "review": "The product has a mixture of good and bad qualities.",
                "model_ids": ["gemini-flash", "mistral-small"],
                "strategy": "parser",
            },
        )
        events = parse_sse(response.text)

        self.assertEqual(sum(name == "model_result" for name, _ in events), 1)
        self.assertEqual(sum(name == "model_error" for name, _ in events), 1)
        self.assertEqual(events[-1][1]["successful"], 1)
        self.assertEqual(events[-1][1]["failed"], 1)


if __name__ == "__main__":
    unittest.main()
