# Package initialization
import os
from dotenv import load_dotenv

# Load .env configuration
load_dotenv()

# Ensure default Vertex AI configuration is loaded if not explicitly set
if "GOOGLE_GENAI_USE_VERTEXAI" not in os.environ:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

from customer_support_agent.agent import root_agent

__all__ = ["root_agent"]
