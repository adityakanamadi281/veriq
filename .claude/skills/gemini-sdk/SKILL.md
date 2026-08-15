---
name: gemini-sdk
description: Use the Google GenAI Python SDK and Gemini Interactions API safely for resume parsing, adaptive questioning, response evaluation, and report generation.
---

# Gemini SDK Skill

## SDK

Use `google-genai`.

Preferred pattern:

```python
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="Explain how AI works in a few words",
)

print(interaction.output_text)
```

Keep the model configurable:

`GEMINI_MODEL=gemini-2.5-flash`

and keep `GEMINI_API_KEY` server-side.

## Service boundary

Create a dedicated service such as:

`backend/app/services/gemini_service.py`

Do not instantiate clients throughout route handlers.

## Prompt contracts

Each use case gets a separate prompt and Pydantic schema:
- resume extraction
- question generation
- response evaluation
- final assessment synthesis

Avoid one giant prompt for the entire application.

## Resume extraction

Input:
- extracted resume text

Output:
- candidate profile fields

Rules:
- preserve facts;
- do not infer unsupported experience;
- use null when unavailable;
- normalize skills conservatively.

## Question generation

Input:
- candidate context
- dimensions
- evidence collected
- missing evidence
- prior questions

Output:
- one question
- target dimension
- question format
- assessment objective
- evaluation criteria

## Response evaluation

Input:
- question
- candidate response
- evaluation criteria
- candidate context

Output:
- evidence
- strengths
- gaps
- dimension score/signal
- confidence
- whether more evidence is needed

## Final synthesis

Use validated intermediate evaluations to create:
- readiness result
- report
- recommendation

Do not allow final synthesis to invent facts not present in the persisted evidence.

## Failure handling

Catch Gemini/API failures and return application-level errors. Never leak API keys or raw provider credentials.

Where useful, retry transient failures with bounded retries.

## Interactions API

The current Google documentation supports the Interactions API through `google-genai`; `output_text` is available as a convenience property. Stateful conversations can use `previous_interaction_id`, but AURA's durable assessment state should remain in Supabase/Postgres rather than relying exclusively on provider-side state.

## Testing

Mock Gemini in unit tests. End-to-end tests may use a real API only when explicitly configured.
