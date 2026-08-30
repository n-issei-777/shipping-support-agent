# Customer Support Agent (Shipping Company)

This project is a customer support agent built for a shipping and logistics company using **Google ADK 2.0 (Agent Development Kit)** Graph Workflows.

> **Reference:** This agent project is based on the Google Developers Codelab:  
> [Antigravity CLI Hands-on](https://codelabs.developers.google.com/antigravity-cli-hands-on#0)

---

## Overview

The Customer Support Agent acts as an automated representative for a parcel shipping company. It intelligently triages user inquiries, invokes specialized domain tools, enforces security guardrails, supports Human-in-the-Loop (HITL) approval workflows, and politely declines unrelated inquiries.

### Key Capabilities

1. **PII Masking & Safety Guardrails**:
   - Automatically redacts sensitive customer data (credit card numbers, email addresses, phone numbers, SSNs) before logging or storage.
   - Detects and blocks prompt injection and instruction-override attacks.
2. **Intent Classification & Strategic Routing**:
   - Classifies user inquiries into shipping topics (*Rates*, *Tracking*, *Delivery*, *Returns*) or *Unrelated*.
   - Uses strategic model routing with fast triage (`gemini-3.5-flash-lite`) and deep reasoning (`gemini-3.7-flash`).
3. **Shipping FAQ Agent & Specialized Tools**:
   - Operates under a comprehensive system constitution prompt defining domain boundaries and behaviors.
   - `calculate_shipping_rates`: Computes transit costs and estimated days by origin/destination ZIP codes and package weight.
   - `track_package_by_number`: Queries shipment milestone status, current location, and estimated delivery dates.
   - `submit_return_request`: Initiates return authorizations with guided error recovery instructions.
4. **Human-in-the-Loop (HITL) Approval Gate**:
   - Flags high-value return requests ($100 or higher) and emits a `RequestInput` approval interrupt for human supervisor authorization.
5. **Polite Decline Handler**:
   - Gracefully declines non-shipping inquiries (e.g., general chit-chat, weather, programming) while clarifying the scope of support.
6. **Observability & Memory Management**:
   - OpenTelemetry distributed tracing linking trace IDs and span contexts across nodes and tools.
   - Structured JSON logging capturing intended actions (*Intent*) before execution and actual results (*Outcome*) after.
   - Context compaction using a sliding-window strategy to prevent context bloat.
   - SQLite persistent session storage and non-blocking asynchronous memory consolidation.

---

## Project Structure

```
test_ship/
├── doc/
│   └── design.md                 # System architecture design & Mermaid diagrams
├── customer_support_agent/
│   ├── __init__.py               # Package initialization
│   ├── agent.py                  # Root agent (ADK 2.0 Workflow graph)
│   ├── classifier.py             # Intent classification & routing node
│   ├── config.py                 # Secure configuration & Vertex AI ADC loader
│   ├── decline.py                # Polite decline handler node
│   ├── guardrails.py             # PII scrubbing & safety guardrails
│   ├── hitl.py                   # Human-in-the-Loop approval gate
│   ├── memory.py                 # History compaction & persistent session store
│   ├── observability.py          # Structured JSON logging & OpenTelemetry tracing
│   ├── prompts.py                # System constitution prompt
│   ├── schemas.py                # Strict Pydantic data schemas
│   ├── shipping_faq.py           # Shipping FAQ agent (gemini-3.7-flash)
│   └── tools.py                  # Domain tools with docstrings & guided error recovery
├── eval/
│   ├── dataset.jsonl             # Golden evaluation dataset
│   └── eval_runner.py            # Automated regression evaluation harness
├── infra/
│   └── terraform/                # Infrastructure as Code (GCP Service Account, Secret Manager)
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── tests/
│   ├── unit/                     # Unit test suite
│   └── integration/              # End-to-end integration test suite
├── .env_example                  # Environment variable template
├── .gitignore                    # Git ignore configuration
├── .python-version               # Python version (3.13)
├── pyproject.toml                # Project configuration and dependencies (uv)
├── run_agent.py                  # Interactive console runner
└── README.md                     # Project documentation
```

---

## Prerequisites

- **Python**: 3.13
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Google Cloud SDK**: `gcloud` authenticated with Vertex AI access

---

## Setup Instructions

### 1. Authentication (Google Cloud Vertex AI ADC)

This project uses Google Cloud Application Default Credentials (ADC) rather than hardcoded API keys:

```bash
gcloud auth application-default login
```

Set the required environment variables (or copy `.env_example` to `.env`):

```bash
export GOOGLE_GENAI_USE_VERTEXAI=True
export GOOGLE_CLOUD_PROJECT=your-gcp-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

### 2. Install Dependencies

Install all dependencies using `uv`:

```bash
uv sync --index https://pypi.org/simple
```

---

## Running Tests & Verification

### 1. Run Unit & Integration Tests

Execute the complete test suite with `pytest`:

```bash
uv run pytest
```

### 2. Run Automated Evaluation Suite

Evaluate the agent against the golden dataset:

```bash
PYTHONPATH=. uv run python3.13 eval/eval_runner.py
```

### 3. Interactive Console Demo

Start the interactive CLI session to chat with the agent:

```bash
uv run python3.13 run_agent.py
```
