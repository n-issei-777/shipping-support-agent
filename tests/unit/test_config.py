# Configuration and secret management unit tests
import os
from unittest.mock import patch

from customer_support_agent.config import AppConfig


class TestSecureSecretManagement:
    # Test secret management and configuration

    def test_default_config_uses_vertex_ai(self):
        # Verify default configuration uses Vertex AI ADC
        config = AppConfig()
        assert config.use_vertexai is True
        assert config.api_key is None

    def test_load_from_environment(self):
        # Verify safe configuration loading from environment variables
        with patch.dict(
            os.environ,
            {
                "GOOGLE_GENAI_USE_VERTEXAI": "True",
                "GOOGLE_CLOUD_PROJECT": "test-shipping-project",
                "GOOGLE_CLOUD_LOCATION": "us-central1",
            },
        ):
            config = AppConfig.from_env()
            assert config.project_id == "test-shipping-project"
            assert config.location == "us-central1"
            assert config.use_vertexai is True
