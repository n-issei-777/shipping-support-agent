# Configuration and secret management module
import os
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    # Application configuration class
    use_vertexai: bool = Field(
        default=True,
        description="Flag indicating whether to use Google Cloud Vertex AI ADC"
    )
    project_id: str | None = Field(
        default=None,
        description="Google Cloud project ID"
    )
    location: str = Field(
        default="us-central1",
        description="Google Cloud region"
    )
    api_key: str | None = Field(
        default=None,
        description="API key (None when Vertex AI ADC is used)"
    )

    @classmethod
    def from_env(cls) -> "AppConfig":
        # Build configuration from environment variables and ADC
        use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() in ("true", "1", "yes")
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        return cls(
            use_vertexai=use_vertex,
            project_id=project,
            location=location,
            api_key=None,
        )
