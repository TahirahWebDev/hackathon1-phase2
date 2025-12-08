# Implementation Plan: AI-native Textbook with RAG Chatbot

**Branch**: `1-textbook-generation` | **Date**: 2025-12-06 | **Spec**: specs/1-textbook-generation/spec.md
**Input**: Feature specification from `/specs/1-textbook-generation/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The AI-native textbook will be built using Docusaurus for a clean web-based interface, providing 6 chapters on Physical AI and Humanoid Robotics. An integrated RAG chatbot, powered by Qdrant, Neon, and FastAPI, will answer questions exclusively from the textbook content using free-tier compatible embeddings. Optional features include Urdu translation and personalized chapters, with authentication required for personalized content.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: TypeScript (Docusaurus), Python (FastAPI)
**Primary Dependencies**: Docusaurus, Qdrant, Neon, FastAPI
**Storage**: Qdrant (vector database), Neon (PostgreSQL)
**Testing**: NEEDS CLARIFICATION
**Target Platform**: Web (Docusaurus), Linux server (RAG backend)
**Project Type**: Web
**Performance Goals**: End-to-end latency for RAG chatbot responses under 5 seconds for 95% of queries.
**Constraints**: No heavy GPU usage, minimal embeddings.
**Scale/Scope**: 6 chapters, free-tier architecture, 99% uptime.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Simplicity: Prioritize clarity and ease of understanding.
- [x] Accuracy: Information presented in textbook and chatbot must be factually correct and reliable.
- [x] Minimalism: Design and implementation should be lean, focusing on essential features.
- [x] Fast Builds: Docusaurus site optimized for rapid build times.
- [x] Free-tier Architecture: All infrastructure and service choices adhere to free-tier limitations.
- [x] RAG Answers ONLY from Book Text: Chatbot uses only textbook content as its knowledge base.

## Project Structure

### Documentation (this feature)

```text
specs/1-textbook-generation/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
```text
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: The project will adopt a web application structure with separate `frontend/` (Docusaurus) and `backend/` (FastAPI, Qdrant, Neon) directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|           |            |                                     |
