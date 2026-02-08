
## Rephrased Request and Intent

The user wants to develop a web application called "Life Manager" that assists users in managing their life goals. This application will leverage AI agents and Large Language Models (LLMs) to facilitate goal clarification, plan creation, and ongoing progress tracking. 

**Here's a breakdown of the key requirements:**

*   **Core Functionality:**
    *   **Goal Definition:**  The application needs to guide users through defining their life goals.
    *   **Actionable Plan Generation:** It should use AI/LLMs to translate these goals into actionable plans.
    *   **Progress Tracking & Feedback Loop:** Implement a system for regular check-ins (e.g., nightly) to collect user feedback on the progress of their plans and automatically adjust the schedule as needed.
*   **Data Management:**
    *   **Storage:** Initially, data will be stored in SQLite. 
    *   **Calendar Synchronization:**  Planned tasks and events must be synced with an external calendar (e.g., Google Calendar or a CalDAV-compatible calendar).
*   **Technical Stack:**
    *   **Frontend:** React + JavaScript
    *   **Backend:** Python with FastAPI
    *   **Authentication:** Simple email/password authentication.

**Assumptions:**

*   The user is familiar with the basic concepts of React, JavaScript, and Python.
*   The user has access to an LLM (e.g., OpenAI, Cohere) for AI-powered assistance.
*   The user will handle the integration with external calendar services (Google Calendar, CalDAV).
*   The application will be designed with a focus on user experience and ease of use.

**Technical Gaps:**

*   Specific LLM integration details (API keys, prompt engineering).
*   Calendar API integration specifics (authentication, event creation/modification).
*   Data validation and error handling strategies.
*   User interface design considerations for goal definition and progress tracking.
```
