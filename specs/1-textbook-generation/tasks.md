# Development Tasks: AI-native Textbook with RAG Chatbot

**Branch**: `1-textbook-generation` | **Date**: 2025-12-06 | **Spec**: specs/1-textbook-generation/spec.md
**Plan**: specs/1-textbook-generation/plan.md

## Summary

This document outlines the detailed development tasks for implementing the AI-native Textbook with RAG Chatbot feature. Tasks are organized by phase and user story, with clear IDs, priorities, and file paths to facilitate independent and sequential execution.

## Phase 1: Setup & Project Initialization
Goal: Establish the basic project structure and development environment.

- [ ] T001 Create project directories: `backend/`, `frontend/`
- [ ] T002 Initialize FastAPI project in `backend/` with `main.py`, `requirements.txt`
- [ ] T003 Initialize Docusaurus project in `frontend/`
- [ ] T004 Configure `backend/requirements.txt` with FastAPI, Uvicorn, Qdrant-client, psycopg2, python-dotenv, httpx, pytest, pytest-asyncio
- [ ] T005 Configure `frontend/package.json` with Docusaurus dependencies, Jest, React Testing Library, Cypress, Playwright
- [ ] T006 Create `backend/.env` file for database and other configurations
- [ ] T007 Create `docker-compose.yaml` in `backend/` for Qdrant and PostgreSQL

## Phase 2: Foundational Components (Blocking Prerequisites)
Goal: Implement core, shared components required by multiple user stories.

- [ ] T008 [P] Implement `Chapter` model in `backend/src/models/chapter.py`
- [ ] T009 [P] Implement `TextbookContent` model in `backend/src/models/textbook_content.py`
- [ ] T010 [P] Implement `UserAccount` model in `backend/src/models/user_account.py`
- [ ] T011 [P] Implement base database connection and session management in `backend/src/database.py`
- [ ] T012 [P] Create utility for embedding generation (e.g., `backend/src/services/embedding_service.py`)
- [ ] T013 Implement CMS ingestion API endpoint (`/cms/ingest`) in `backend/src/api/cms.py` based on `contracts/openapi.yaml`
- [ ] T014 Implement background task for processing ingested content and generating embeddings in `backend/src/services/content_processor.py`

## Phase 3: User Story 1 - Read Textbook Content (P1)
Goal: Enable users to read textbook chapters through the Docusaurus frontend.
Independent Test: The Docusaurus site can be deployed, and a user can navigate through all chapters and view their content.

- [ ] T015 [P] [US1] Create Docusaurus pages for 6 textbook chapters in `frontend/docs/`
- [ ] T016 [US1] Configure Docusaurus `sidebars.js` for automatic sidebar generation in `frontend/sidebars.js`
- [ ] T017 [US1] Implement Docusaurus theme overrides/components for clean display (if necessary) in `frontend/src/theme/`
- [ ] T018 [US1] Verify Docusaurus deployment to GitHub Pages (configuration in `frontend/docusaurus.config.js`)

## Phase 4: User Story 2 - Interact with RAG Chatbot for Q&A (P1)
Goal: Allow students to ask questions and receive answers based solely on textbook content.
Independent Test: The Docusaurus site and RAG chatbot backend can be deployed. A user can ask a question, and the chatbot provides an accurate answer sourced exclusively from the textbook content.

- [ ] T019 [P] [US2] Implement `UserQuery` model in `backend/src/models/user_query.py`
- [ ] T020 [P] [US2] Implement `ChatbotResponse` model in `backend/src/models/chatbot_response.py`
- [ ] T021 [US2] Implement RAG query logic in `backend/src/services/rag_service.py` (query Qdrant, retrieve content, formulate response)
- [ ] T022 [US2] Implement chatbot API endpoint (`/chat`) in `backend/src/api/chat.py` based on `contracts/openapi.yaml`
- [ ] T023 [US2] Integrate chatbot API client in Docusaurus frontend in `frontend/src/components/Chatbot.tsx`
- [ ] T024 [US2] Create Chatbot UI component in `frontend/src/components/Chatbot.tsx`

## Phase 5: User Story 3 - Select Text and Ask AI (P2)
Goal: Enable students to select text and ask context-aware questions to the chatbot.
Independent Test: A user can select text on the Docusaurus site, and a context-aware question can be sent to the chatbot, which responds based on the selected text and overall textbook content.

- [ ] T025 [P] [US3] Implement text selection listener in Docusaurus frontend in `frontend/src/theme/DocItem/Content/index.js` (or similar location for content display)
- [ ] T026 [P] [US3] Display "Ask AI" option on text selection in `frontend/src/components/TextSelectionMenu.tsx`
- [ ] T027 [US3] Modify chatbot API client to send selected context with query in `frontend/src/components/Chatbot.tsx`
- [ ] T028 [US3] Update RAG query logic to incorporate selected text context in `backend/src/services/rag_service.py`

## Phase 6: User Story 4 - Urdu Translation (P3)
Goal: Provide optional Urdu translation for textbook content and chatbot responses.
Independent Test: A user can select Urdu as a language, and the textbook content and/or chatbot responses are displayed in Urdu.

- [ ] T029 [P] [US4] Implement i18n configuration for Docusaurus in `frontend/docusaurus.config.js` and `frontend/i18n/ur/`
- [ ] T030 [P] [US4] Integrate translation service (if external) or logic for chatbot responses in `backend/src/services/translation_service.py`
- [ ] T031 [US4] Add language selection UI in Docusaurus frontend in `frontend/src/components/LanguageSelector.tsx`
- [ ] T032 [US4] Update chatbot response handling to display translated text in `frontend/src/components/Chatbot.tsx`
- [ ] T033 [US4] Update CMS ingestion to support multi-language content (if necessary) in `backend/src/api/cms.py`

## Phase 7: User Story 5 - Personalized Chapter (P3)
Goal: Offer a personalized chapter experience based on user preferences.
Independent Test: A user can configure personalization settings, and a chapter's content or examples are dynamically adjusted based on these settings.

- [ ] T034 [P] [US5] Implement `UserPreferences` model in `backend/src/models/user_preferences.py`
- [ ] T035 [P] [US5] Implement user authentication endpoints (login, register) in `backend/src/api/auth.py`
- [ ] T036 [P] [US5] Implement personalization preferences API (`/personalize/preferences`) in `backend/src/api/personalization.py` based on `contracts/openapi.yaml`
- [ ] T037 [US5] Create authentication context/service in Docusaurus frontend in `frontend/src/contexts/AuthContext.tsx`
- [ ] T038 [US5] Create UI for managing personalization preferences in `frontend/src/pages/preferences.tsx`
- [ ] T039 [US5] Implement logic to adapt chapter content based on user preferences in `frontend/src/theme/DocItem/Content/index.js`
- [ ] T040 [US5] Secure personalized features with authentication middleware in `backend/src/middleware/auth.py`

## Phase 8: Polish & Cross-Cutting Concerns
Goal: Ensure overall quality, performance, and maintainability of the application.

- [ ] T041 Implement unit tests for backend models and services in `backend/tests/unit/`
- [ ] T042 Implement integration tests for backend API endpoints using `TestClient` in `backend/tests/integration/`
- [ ] T043 Implement unit tests for frontend components and utilities in `frontend/src/components/__tests__/`
- [ ] T044 Implement E2E tests using Cypress or Playwright for critical user flows in `e2e_tests/`
- [ ] T045 Configure CI/CD pipelines for automated testing and deployment to GitHub Pages
- [ ] T046 Review and optimize performance for both frontend and backend
- [ ] T047 Implement logging and monitoring for the backend application
- [ ] T048 Create comprehensive READMEs for both `backend/` and `frontend/` directories

## Dependencies

- Phase 1 (Setup) -> Phase 2 (Foundational)
- Phase 2 (Foundational) -> All User Story Phases (3-7)
- User Story Phases are largely independent but rely on foundational components.
- Phase 8 (Polish) depends on all previous phases.

## Parallel Execution Opportunities

**Within Phases:**
- **Phase 2:** T008, T009, T010, T011, T012 can be implemented in parallel.
- **Phase 3:** T015 can be parallelized.
- **Phase 4:** T019, T020 can be parallelized.
- **Phase 5:** T025, T026 can be parallelized.
- **Phase 6:** T029, T030 can be parallelized.
- **Phase 7:** T034, T035, T036 can be parallelized.
- **Phase 8:** All testing tasks (T041, T042, T043, T044) can be developed in parallel.

## Implementation Strategy (MVP First)

The Minimum Viable Product (MVP) will focus on delivering User Story 1 (Read Textbook Content) and User Story 2 (Interact with RAG Chatbot for Q&A). This provides core textbook content consumption and interactive learning, serving as a strong foundation for future enhancements. Subsequent user stories will be implemented incrementally based on priority.