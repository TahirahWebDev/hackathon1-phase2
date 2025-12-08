# Data Model: AI-native Textbook with RAG Chatbot

This document outlines the key entities and their relationships for the AI-native Textbook with RAG Chatbot feature, based on the feature specification.

## Entities

### 1. Chapter
- **Description**: Represents a section of the textbook.
- **Fields**:
    - `id` (string, primary key)
    - `title` (string)
    - `content` (string, markdown/HTML)
    - `sub_sections` (array of strings, optional)
- **Relationships**: One-to-many with `Textbook Content` (a Chapter contributes to Textbook Content).

### 2. Textbook Content
- **Description**: The raw textual data from all chapters, forming the knowledge base for the RAG system.
- **Fields**:
    - `id` (string, primary key)
    - `chapter_id` (string, foreign key to Chapter)
    - `text` (string)
    - `processed_at` (timestamp)
- **Relationships**: Many-to-one with `Chapter`, One-to-many with `Embeddings`.

### 3. User Query
- **Description**: Text input from the user for the RAG chatbot.
- **Fields**:
    - `id` (string, primary key)
    - `user_id` (string, foreign key to User Account, optional)
    - `query_text` (string)
    - `timestamp` (timestamp)
    - `context_text` (string, optional, for 'Select Text and Ask AI' feature)
- **Relationships**: Many-to-one with `User Account`.

### 4. Chatbot Response
- **Description**: Text output from the RAG chatbot.
- **Fields**:
    - `id` (string, primary key)
    - `query_id` (string, foreign key to User Query)
    - `response_text` (string)
    - `source_content_ids` (array of strings, references to relevant Textbook Content)
    - `timestamp` (timestamp)
    - `language` (string, e.g., 'en', 'ur', for translation)
- **Relationships**: One-to-one with `User Query`.

### 5. Embeddings
- **Description**: Vector representations of textbook content for semantic search.
- **Fields**:
    - `id` (string, primary key)
    - `content_id` (string, foreign key to Textbook Content)
    - `vector` (array of floats)
    - `model_version` (string)
- **Relationships**: Many-to-one with `Textbook Content`.

### 6. User Preferences
- **Description**: (For optional personalization) Data representing a user's learning style or preferred content adaptations.
- **Fields**:
    - `user_id` (string, primary key, foreign key to User Account)
    - `learning_style` (string, e.g., 'visual', 'auditory')
    - `preferred_examples` (array of strings, e.g., 'code-heavy', 'conceptual')
    - `language_preference` (string, e.g., 'ur', 'en')
- **Relationships**: One-to-one with `User Account`.

### 7. User Account
- **Description**: (For authenticated features) Represents a user with credentials and associated preferences.
- **Fields**:
    - `id` (string, primary key)
    - `username` (string, unique)
    - `email` (string, unique)
    - `password_hash` (string)
    - `created_at` (timestamp)
- **Relationships**: One-to-one with `User Preferences`, One-to-many with `User Query`.
