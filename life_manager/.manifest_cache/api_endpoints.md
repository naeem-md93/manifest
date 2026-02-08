
# Life Manager API Endpoints

This document outlines the proposed API endpoints for the "Life Manager" application, based on the provided project requirements.  It uses a RESTful API design with standard HTTP methods.

## Authentication

*   **`POST /auth/register`**: Registers a new user.
    *   **Request Body:** `{ "email": "string", "password": "string", "username": "string" }`
    *   **Response:** `201 Created` with a JSON body containing the user's ID and authentication token.
*   **`POST /auth/login`**: Logs in an existing user.
    *   **Request Body:** `{ "email": "string", "password": "string" }`
    *   **Response:** `200 OK` with a JSON body containing the user's ID and authentication token.
*   **`POST /auth/logout`**: Logs out the current user.
    *   **Request Body:** `{ "token": "string" }`
    *   **Response:** `200 OK`

## Goals

*   **`GET /goals`**: Retrieves a list of all goals for the authenticated user.
    *   **Response:** `200 OK` with a JSON body containing an array of goal objects. Each object should include: `id`, `user_id`, `name`, `description`, `status` (e.g., "active", "completed"), `created_at`, `updated_at`.
*   **`POST /goals`**: Creates a new goal for the authenticated user.
    *   **Request Body:** `{ "name": "string", "description": "string", "target_date": "string" }` (e.g., "2024-12-31")
    *   **Response:** `201 Created` with a JSON body containing the newly created goal object and its ID.
*   **`GET /goals/{goal_id}`**: Retrieves a specific goal by its ID.
    *   **Response:** `200 OK` with a JSON body containing the goal object.
*   **`PUT /goals/{goal_id}`**: Updates an existing goal.
    *   **Request Body:** `{ "name": "string", "description": "string", "target_date": "string" }`
    *   **Response:** `200 OK` with a JSON body containing the updated goal object and its ID.
*   **`DELETE /goals/{goal_id}`**: Deletes a goal.
    *   **Response:** `204 No Content`

## Plans

*   **`GET /goals/{goal_id}/plans`**: Retrieves all plans associated with a specific goal.
    *   **Response:** `200 OK` with a JSON body containing an array of plan objects. Each object should include: `id`, `goal_id`, `name`, `description`, `status` (e.g., "draft", "in progress", "completed"), `created_at`, `updated_at`.
*   **`POST /goals/{goal_id}/plans`**: Creates a new plan for a specific goal.
    *   **Request Body:** `{ "name": "string", "description": "string" }`
    *   **Response:** `201 Created` with a JSON body containing the newly created plan object and its ID.
*   **`GET /goals/{goal_id}/plans/{plan_id}`**: Retrieves a specific plan by its ID.
    *   **Response:** `200 OK` with a JSON body containing the plan object.
*   **`PUT /goals/{goal_id}/plans/{plan_id}`**: Updates an existing plan.
    *   **Request Body:** `{ "name": "string", "description": "string" }`
    *   **Response:** `200 OK` with a JSON body containing the updated plan object and its ID.
*   **`DELETE /goals/{goal_id}/plans/{plan_id}`**: Deletes a plan.
    *   **Response:** `204 No Content`

## Progress Tracking

*   **`POST /goals/{goal_id}/progress`**:  Submits progress updates for a goal. This endpoint will be used to receive user feedback on the progress of their plans and automatically adjust the schedule as needed.
    *   **Request Body:** `{ "plan_id": "string", "status": "string" }` (e.g., "completed", "partially completed")
    *   **Response:** `200 OK` with a JSON body containing the updated goal object and its ID.  The response should include a success indicator.

## Calendar Integration

*   **`POST /goals/{goal_id}/events`**: Creates a new event in the user's calendar based on a plan.
    *   **Request Body:** `{ "plan_id": "string", "start_time": "string", "end_time": "string" }` (e.g., "2024-12-25 09:00:00")
    *   **Response:** `201 Created` with a JSON body containing the event ID and details.  The response should include a success indicator.
*   **`GET /goals/{goal_id}/events`**: Retrieves all events associated with a goal.
    *   **Response:** `200 OK` with a JSON body containing an array of event objects. Each object should include: `id`, `user_id`, `goal_id`, `start_time`, `end_time`, `description`.

## LLM Integration (Conceptual)

*   **`POST /goals/{goal_id}/generate_plan`**:  Generates an actionable plan for a goal using an LLM.
    *   **Request Body:** `{ "goal_name": "string", "description": "string" }`
    *   **Response:** `200 OK` with a JSON body containing the generated plan (a string).

## Error Handling

*   All endpoints should return appropriate HTTP status codes to indicate success or failure.
*   Error responses should include a JSON body with a `message` field describing the error.  Example: `{ "message": "Invalid input" }`.



## Notes

*   This is a basic set of endpoints and can be extended as needed.
*   Consider adding pagination to endpoints that return large lists (e.g., `/goals`, `/goals/{goal_id}/plans`).
*   Implement input validation to prevent invalid data from being stored in the database.
*   Use appropriate error handling and logging throughout the application.

</OUTPUT>
