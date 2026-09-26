# Code Reviewr

AI-powered sequential code engineering assistant.

Built by Vishnu.

## Features

- Sequential workflow: Code Builder → Code Reviewer → Code Refactorer
- LangChain-based OpenAI integration using `ChatOpenAI` and `PromptTemplate`
- Strong separation between generation, review, and refactoring
- Structured Pydantic models for reliable agent outputs
- Streamlit-based developer tool interface
- Safe handling of LLM responses with JSON parsing and validation
- Clean dependency management and environment-based secrets
- Download support for generated code, refactored code, and review reports
- Reset and session-state persistence without exposing secrets
- Conditional API-key gating so the app warns clearly if OpenAI credentials are missing

## Architecture

The app is organized into small, focused modules:

- `app.py` — Streamlit user interface and workflow orchestration entry point
- `agents/` — specialized agents for building, reviewing, and refactoring code
- `workflow/` — orchestrator and state management for the sequential process
- `models/` — Pydantic schemas for the workflow outputs
- `services/` — LLM abstraction layer and provider isolation
- `prompts/` — dedicated system prompts and user prompt builders
- `utils/` — shared logging configuration

## Agent workflow

1. Code Builder receives the user requirements and produces code.
2. The generated code becomes the input to the Code Reviewer.
3. The reviewer produces findings and a structured review result.
4. The Code Refactorer receives the original requirement, the generated code, and the review findings.
5. The final refactored code is returned to the user.

This is a true sequential workflow, not three independent prompt calls.

## Project structure

```text
code-reviewr/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── agents/
│   ├── __init__.py
│   ├── code_builder.py
│   ├── code_reviewer.py
│   └── code_refactorer.py
├── workflow/
│   ├── __init__.py
│   ├── orchestrator.py
│   └── state.py
├── models/
│   ├── __init__.py
│   └── schemas.py
├── services/
│   ├── __init__.py
│   └── llm_service.py
├── prompts/
│   ├── __init__.py
│   ├── code_builder_prompt.py
│   ├── code_reviewer_prompt.py
│   └── code_refactorer_prompt.py
├── utils/
│   ├── __init__.py
│   └── logging_config.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_workflow.py
    └── test_agents.py
```

## Requirements

- Python 3.11+
- Streamlit
- LangChain
- LangChain OpenAI
- LangChain Core
- Pydantic
- python-dotenv
- OpenAI API key for runtime use

## Installation

```bash
git clone <repository>
cd code-reviewr
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Environment setup

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Then update it with your values:

```env
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o-mini
DEFAULT_TEMPERATURE=0.2
DEFAULT_MAX_TOKENS=2000
```

The app also accepts `LLM_API_KEY` as a fallback for compatibility, but `OPENAI_API_KEY` is the recommended environment variable because it matches the LangChain OpenAI integration pattern used in the reference project.

Do not hard-code API keys in the codebase. The app reads them from environment variables only.

## Configuration

The application uses:

- `OPENAI_API_KEY` as the primary key for the LangChain OpenAI client
- `LLM_API_KEY` as a fallback alias for compatibility
- `LLM_MODEL` to choose the model
- `DEFAULT_TEMPERATURE` and `DEFAULT_MAX_TOKENS` as defaults

## Running the application

```bash
streamlit run app.py
```

Then open the local Streamlit URL in your browser.

## Example usage

Use the sidebar to set:

- Project / Task Name: `API utility`
- Language: `Python`
- Requirement: `Build a Python script that reads a CSV file and summarizes the top 10 values by column.`
- Additional Instructions: `Use standard library only and keep the code easy to read.`

Then click `Start Workflow`.

## Security considerations

- API keys are never hard-coded into the application.
- Secret values are never displayed in the UI.
- Generated code is never executed automatically.
- The app logs workflow events without exposing full sensitive payloads.
- If execution support is added in the future, it must be sandboxed.

## Troubleshooting

### Model errors

If you see a missing API key warning or error:

1. Confirm your `.env` file exists.
2. Ensure the key is set under `OPENAI_API_KEY`.
3. You may also use `LLM_API_KEY` as a compatibility fallback.
4. Restart the Streamlit process after editing environment values.

The app intentionally checks for the key before starting the workflow and shows a clean warning without exposing sensitive information.

### JSON parse errors

The LLM service includes safe parsing and a fallback extraction path. If a model returns malformed JSON, the service attempts to recover the structured payload. If the output still cannot be parsed, the workflow exits with a clear error.

### Missing dependencies

Run:

```bash
pip install -r requirements.txt
```

## Future enhancements

- Custom provider integrations beyond OpenAI
- Token and cost estimation
- PDF or markdown export of the full workflow
- Better language detection and code-language presets
- Team-friendly project save/load workflows
- More detailed review scoring and severity analytics

## License

This project is provided for educational and portfolio use.
