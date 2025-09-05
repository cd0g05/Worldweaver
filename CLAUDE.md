# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WorldWeaver is a Flask-based web application for story planning with AI assistance. It features a React frontend with real-time document editing and an AI chat interface, backed by a Python Flask server that integrates with multiple LLM providers (Google Vertex AI and OpenAI).

## Development Commands

### Backend (Python/Flask)
- **Start development server**: `python main.py` (runs on debug mode by default)
- **Install dependencies**: Install using pip from `requirements.txt` or use `uv` with `pyproject.toml`
- **Create test user**: The main.py automatically creates a test user (t@t.t / pwd) on startup

### Frontend (React/Vite)
- **Development mode**: `cd frontend/planner && npm run dev` (runs on localhost:5173)
- **Build for production**: `cd frontend/planner && npm run build`
- **Lint code**: `cd frontend/planner && npm run lint`
- **Preview production build**: `cd frontend/planner && npm run preview`

### Environment Setup
- Set `DEV_MODE=1` environment variable to redirect planning route to Vite dev server
- Required environment variables:
  - `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID
  - `ANTHROPIC_SONNET_FOUR_LOCATION` / `GEMINI_LOCATION`: Vertex AI regions
  - `ANTRHOPIC_SONNET_FOUR_ID` / `GEMINI_PRO_2_5_ID`: Model IDs
  - `OPENAI_API_KEY`: OpenAI API key

## Architecture Overview

### Backend Structure
- **Agent System** (`backend/agents/`): Modular AI agent architecture supporting multiple LLM providers
  - `Agent` (base class): Abstract base for all AI agents
  - `GoogleVertexAIAgent`: Vertex AI implementation with templated prompts
  - `AgentMap`: Maps stage numbers to prompt configurations
  - `Processor`: Orchestrates agent selection and response handling
  - `CurrentAgent`: Tracks current conversation stage/context

- **Prompt Management** (`backend/config/prompts/`): TOML-based versioned prompts
  - Format: `{name}.toml` with versioned sections (v1, v2, etc.)
  - Supports template placeholders: `{chat}`, `{doc}` for context injection

- **Flask Routes** (`frontend/scripts/routes.py`): Main application routes
  - `/planning`: Serves React SPA (redirects to Vite in dev mode)
  - `/llm`: JSON API endpoint for AI chat functionality
  - Authentication via Flask-Login with SQLite backend

### Frontend Structure
- **React SPA** (`frontend/planner/src/`): Vite-based React application
  - `PlannerPage.jsx`: Main layout with document editor and chat panel
  - `DocEditor.jsx`: TipTap-based rich text editor
  - `LLMChatPanel.jsx`: Chat interface with tool execution capabilities
  - **Tool System**: AI can execute document operations (insert, delete, format, etc.)

- **Build System**: Vite with Tailwind CSS, outputs to `frontend/static/planning-dist/`

### Key Integration Points
- **Document Context**: Editor content sent to AI via `/llm` endpoint in JSON format
- **Chat History**: Full conversation context maintained and sent with each AI request
- **Tool Execution**: AI responses parsed as either messages or tool commands that modify the document
- **Stage Management**: UI tracks current planning stage, which determines which AI prompt/agent to use

### Database
- **SQLite** (`mydb.sqlite`): Simple user authentication with SQLAlchemy
- **Models** (`frontend/scripts/dbmodels.py`): User model with Flask-Login integration

## Development Notes

- The application uses a dual-mode setup: Flask serves the API and static files, while Vite serves the React app in development
- AI responses can be either plain text messages or structured tool commands (JSON)
- The agent system is designed to support different conversation stages/contexts through prompt switching
- Document editing uses TipTap editor with custom tool integration for AI-driven content modifications