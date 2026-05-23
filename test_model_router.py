import unittest
from unittest.mock import MagicMock, patch

from modules.llm_router import ModelRouter


class TestModelRouter(unittest.TestCase):
    @patch("modules.llm_router.generate_with_ollama")
    def test_ollama_route_uses_local_helper(self, mock_generate):
        mock_generate.return_value = "local response"

        router = ModelRouter(provider="ollama", model_name="llama3.1:8b")
        result = router.generate("hello", temperature=0.2, max_tokens=128)

        self.assertEqual(result, "local response")
        mock_generate.assert_called_once_with(
            "hello",
            model="llama3.1:8b",
            temperature=0.2,
            max_tokens=128,
        )

    @patch("modules.llm_router.GeminiLLM")
    def test_gemini_route_uses_gemini_wrapper(self, mock_gemini_cls):
        llm = MagicMock()
        llm.generate.return_value = "gemini response"
        mock_gemini_cls.return_value = llm

        router = ModelRouter(
            provider="gemini",
            model_name="gemini-2.5-flash",
            api_key="test-key",
        )
        result = router.generate("hello", temperature=0.1)

        self.assertEqual(result, "gemini response")
        mock_gemini_cls.assert_called_once_with(
            api_key="test-key",
            model_name="gemini-2.5-flash",
        )
        llm.generate.assert_called_once_with(
            "hello",
            system_prompt=None,
            temperature=0.1,
            max_tokens=8192,
        )


if __name__ == "__main__":
    unittest.main()
