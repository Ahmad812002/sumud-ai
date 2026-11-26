import asyncio, clients.llm as llm
import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from clients.llm import llm_chat_stream

os.environ.setdefault("GEMINI_API_KEY", "fake-test-key")
os.environ.setdefault("NOMIC_API_KEY", "fake-test-key")

fake_nomic = SimpleNamespace(
    login=lambda token=None: None,
    embed=SimpleNamespace(
        text=lambda **kwargs: {"embeddings": [[0.1, 0.2]]}
    ),
)
sys.modules.setdefault("nomic", fake_nomic)

from business_logic import llm
from routers.chat import ChatRequest, chat_stream


class FakeCompletions:
    def create(self, **kwargs):
        assert kwargs["stream"] is True
        return iter([
            SimpleNamespace(choices=[
                SimpleNamespace(delta=SimpleNamespace(content="Hello "))
            ]),
            SimpleNamespace(choices=[
                SimpleNamespace(delta=SimpleNamespace(content="from "))
            ]),
            SimpleNamespace(choices=[
                SimpleNamespace(delta=SimpleNamespace(content="the fake LLM"))
            ]),
        ])


class FakeClient:
    chat = SimpleNamespace(completions=FakeCompletions())


class ChatStreamingTests(unittest.TestCase):
    def test_llm_stream_yields_fake_delta_chunks(self):
        with patch.object(llm, "client", FakeClient()):
            chunks = list(llm_chat_stream("Test prompt", "Test message"))

        self.assertEqual(chunks, ["Hello ", "from ", "the fake LLM"])

    def test_sse_endpoint_emits_deltas_and_done_marker(self):
        async def run():
            with (
                patch(
                    "business_logic.chat_logic.get_embedding",
                    return_value=[0.1, 0.2],
                ),
                patch(
                    "business_logic.chat_logic.get_embedding_result",
                    return_value=[{"documents": "Fake profile evidence"}],
                ),
                patch.object(llm, "client", FakeClient()),
            ):
                response = await chat_stream(ChatRequest(message="Test message"))

                events = []
                async for chunk in response.body_iterator:
                    events.append(chunk)
                return response, events

        response, events = asyncio.run(run())
        self.assertEqual(response.media_type, "text/event-stream")

        data_events = [event for event in events if event.startswith("data: ")]
        payloads = []
        for event in data_events:
            data = event.removeprefix("data: ").strip()
            if data == "[DONE]":
                continue
            payloads.append(json.loads(data))

        self.assertEqual(
            "".join(payload["delta"] for payload in payloads),
            "Hello from the fake LLM",
        )
        self.assertTrue(events[-1].strip().endswith("[DONE]"))


if __name__ == "__main__":
    unittest.main()
