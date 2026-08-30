# Customer Support Agent - Architecture & Design Document

## 1. Overview

This project (`customer-support-agent`) is an enterprise-grade customer support agent built for a shipping and logistics company using **Google ADK 2.0 (Agent Development Kit)** Graph Workflows.
It provides multi-layered query classification, input guardrails, domain-specialized tools, Human-in-the-Loop (HITL) approval workflows, and polite decline routing for out-of-domain inquiries. The runtime environment is built on **Python 3.13**.

## 2. System Architecture

```mermaid
flowchart TD
    User([User Request]) --> PIIIn[PII Scrubber & Guardrail]
    PIIIn --> START([Workflow START])
    
    START --> Classifier["Classifier Node<br>(Strategic Routing: gemini-3.5-flash-lite)"]
    
    Classifier -->|route: shipping_faq| FAQAgent["Shipping FAQ Agent<br>(gemini-3.7-flash)"]
    Classifier -->|route: decline| DeclineNode["Decline Handler Node<br>(Polite Refusal)"]
    
    subgraph Tools ["Specialized Shipping Tools (Explicit JSON Schemas & Docstrings)"]
        RatesTool["calculate_shipping_rates"]
        TrackTool["track_package_by_number"]
        ReturnTool["submit_return_request"]
    end
    
    FAQAgent --> Tools
    ReturnTool -->|High-stakes >= $100| HITL["Human-in-the-Loop Gate<br>(RequestInput)"]
    HITL -->|Human Approved| ReturnApproved[Process Return]
    HITL -->|Human Rejected| ReturnRejected[Decline Return]
    
    subgraph Observability ["Observability & Memory Layer"]
        OTel[OpenTelemetry Tracing]
        JSONLog[Structured JSON Logger]
        PIIScrub[PII Redactor]
        Compactor[History Compactor]
        AsyncMem[Async Memory Persistence]
    end
    
    FAQAgent -.-> Observability
    DeclineNode -.-> Observability
```

## 3. Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Guardrail as Input Guardrail & PII Scrubber
    participant Workflow as Graph Workflow (ADK 2.0)
    participant OTel as OpenTelemetry Tracer
    participant Classifier as Classifier (gemini-3.5-flash-lite)
    participant FAQ as Shipping FAQ Agent (gemini-3.7-flash)
    participant Tools as Shipping Tools
    participant HITL as HITL Approval Gate
    actor Supervisor as Human Supervisor
    participant Mem as Async Memory & JSON Logger

    User->>Guardrail: Send Customer Query
    Guardrail->>Guardrail: PII Masking & Prompt Injection Check
    Guardrail->>Workflow: Sanitized Input Content
    Workflow->>OTel: Start Span (Generate trace_id)
    
    Workflow->>Classifier: Triage Query Intent
    Classifier-->>Workflow: Event(route="shipping_faq" | "decline")
    
    alt route == "shipping_faq" (Shipping Related)
        Workflow->>FAQ: Process Query (Apply System Constitution)
        opt Tool Execution Required
            FAQ->>Tools: calculate_shipping_rates / track_package_by_number
            Tools-->>FAQ: Structured Response (with Guided Error Recovery)
        end
        opt High-Value Return (>= $100)
            FAQ->>HITL: submit_return_request (High Value)
            HITL->>Supervisor: Request Approval (RequestInput Interrupt)
            Supervisor-->>HITL: Approved / Rejected
            HITL-->>FAQ: Authorization Outcome
        end
        FAQ-->>Workflow: Final FAQ Answer (ShippingFaqResponse)
    else route == "decline" (Out of Scope)
        Workflow->>Workflow: Execute Decline Handler
    end
    
    Workflow->>OTel: End Span
    Workflow->>Mem: Async Memory Consolidation & Structured JSON Logging
    Workflow-->>User: Return Final Response
```

## 4. Component Details

### 4.1 Input Guardrails & PII Scrubber (`guardrails.py`)
- Regular expression redaction for credit cards, email addresses, phone numbers, and Social Security Numbers (SSNs).
- Detects and blocks prompt injection and system instruction override attacks.

### 4.2 Classifier Node (`classifier.py`)
- Evaluates user input messages and emits routing events (`route="shipping_faq"` or `route="decline"`).
- Shipping topics supported: Rates, Tracking, Delivery scheduling, and Returns.

### 4.3 Shipping FAQ Agent & Tools (`shipping_faq.py`, `tools.py`)
- Built with `LlmAgent` powered by `gemini-3.7-flash` and guided by the system constitution (`prompts.py`).
- Tools:
  - `calculate_shipping_rates`: Calculates estimated cost and delivery timeframe based on ZIP codes and weight.
  - `track_package_by_number`: Queries tracking database for shipment milestone, location, and ETA.
  - `submit_return_request`: Registers return requests with guided recovery instructions.

### 4.4 Human-in-the-Loop Gate (`hitl.py`)
- Emits `RequestInput` interrupts for return requests exceeding the $100 threshold, requiring explicit human supervisor authorization.

### 4.5 Observability & Memory (`observability.py`, `memory.py`)
- Distributed tracing using OpenTelemetry (`trace_id` and `span_id` propagation).
- Structured JSON logger recording execution intent before tool execution and outcome afterward.
- Sliding-window context compaction preventing token explosion in long conversation turns.
- SQLite-backed session persistence with non-blocking asynchronous memory consolidation.

## 5. Security & Authentication (Vertex AI ADC)

The system leverages Google Cloud Vertex AI Application Default Credentials (ADC), eliminating hardcoded API keys. It also supports secure configuration retrieval via Google Cloud Secret Manager.
