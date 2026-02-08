
# Life Manager Database Schema

## Database Schema Proposal

This document outlines a database schema for the "Life Manager" application, designed for simplicity and ease of understanding.  It leverages SQLite as specified in the project document.

### Tables

We will use the following tables:

1.  **Users:** Stores user account information.
2.  **Goals:** Represents individual life goals.
3.  **Goal_Steps:**  Represents the steps required to achieve a goal.
4.  **Actions:** Stores actions related to specific steps (e.g., tasks, appointments).
5.  **Progress:** Tracks progress against goals and steps.
6.  **Calendar_Events:** Stores events synced from external calendars.

## Table Details

### 1. Users

*   **Table Name:** `users`
*   **Columns:**
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique identifier for each user.
    *   `email` (TEXT UNIQUE NOT NULL) - User's email address (used for login).
    *   `password` (TEXT NOT NULL) - Hashed password.
    *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP) - Timestamp of account creation.

### 2. Goals

*   **Table Name:** `goals`
*   **Columns:**
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique identifier for each goal.
    *   `user_id` (INTEGER NOT NULL) - Foreign key referencing the `users` table.
    *   `name` (TEXT NOT NULL) -  The name of the goal (e.g., "Learn to code", "Run a marathon").
    *   `description` (TEXT) - A more detailed description of the goal.
    *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP) - Timestamp of goal creation.
    *   `status` (TEXT DEFAULT 'active') - Status of the goal (e.g., 'active', 'completed', 'paused').

### 3. Goal_Steps

*   **Table Name:** `goal_steps`
*   **Columns:**
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique identifier for each step.
    *   `goal_id` (INTEGER NOT NULL) - Foreign key referencing the `goals` table.
    *   `step_name` (TEXT NOT NULL) - Name of the step (e.g., "Complete online course", "Train 3 times a week").
    *   `description` (TEXT) - Description of the step.
    *   `order` (INTEGER NOT NULL) - Order of the step within the goal.

### 4. Actions

*   **Table Name:** `actions`
*   **Columns:**
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique identifier for each action.
    *   `goal_step_id` (INTEGER NOT NULL) - Foreign key referencing the `goal_steps` table.
    *   `description` (TEXT NOT NULL) - Description of the action (e.g., "Watch video", "Buy equipment").
    *   `due_date` (DATE) - The due date for the action.
    *   `completed` (BOOLEAN DEFAULT FALSE) - Indicates whether the action has been completed.

### 5. Progress

*   **Table Name:** `progress`
*   **Columns:**
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique identifier for each progress record.
    *   `goal_id` (INTEGER NOT NULL) - Foreign key referencing the `goals` table.
    *   `step_id` (INTEGER NOT NULL) - Foreign key referencing the `goal_steps` table.
    *   `date` (DATE) - The date the progress was recorded.
    *   `notes` (TEXT) - Any notes about the progress made on that day.

### 6. Calendar_Events

*   **Table Name:** `calendar_events`
*   **Columns:**
    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique identifier for each event.
    *   `user_id` (INTEGER NOT NULL) - Foreign key referencing the `users` table.
    *   `event_name` (TEXT NOT NULL) - Name of the event.
    *   `description` (TEXT) - Description of the event.
    *   `start_time` (TIME) - Event start time.
    *   `end_time` (TIME) - Event end time.
    *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

## Relationships

*   **Users** 1:N **Goals** (One user can have multiple goals)
*   **Goals** 1:N **Goal\_Steps** (One goal can have multiple steps)
*   **Goal\_Steps** 1:N **Actions** (One step can have multiple actions)
*   **Goals** 1:N **Progress** (One goal can have multiple progress records)
*   **Goal\_Steps** 1:N **Progress** (One step can have multiple progress records)
*   **Users** 1:N **Calendar\_Events** (One user can have multiple calendar events)

## Data Types

The data types specified above are indicative and may need to be adjusted based on the specific requirements of the application.  `TEXT` is used for string values, `INTEGER` for integer values, `TIMESTAMP` for date and time, and `DATE` for dates. `BOOLEAN` is used for true/false values.

## Considerations

*   **Indexing:**  Indexes should be created on foreign key columns (`user_id`, `goal_id`, `goal_step_id`) to improve query performance.
*   **Data Validation:** Implement data validation rules to ensure data integrity (e.g., required fields, valid date formats).
*   **Scalability:**  Consider database scaling strategies if the application is expected to handle a large number of users and goals.
*    **Calendar API Integration**: The `calendar_events` table will be used to store events synced from external calendars. This allows for easy retrieval and management of calendar events within the application.

This schema provides a solid foundation for the "Life Manager" application. Further refinement may be necessary based on specific implementation details and evolving requirements.
