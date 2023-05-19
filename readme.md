# To-Do List API

## Project Purpose

The purpose of this project is to provide a RESTful API for a to-do list application. This API allows users to manage their to-do tasks by providing functionalities to add, retrieve, update, and delete tasks. The API is built using Flask and the data is stored in a MySQL database.

## Tech Stack

- **Flask**: Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.

- **MySQL**: MySQL is a freely available open-source Relational Database Management System (RDBMS) that uses Structured Query Language (SQL). SQL is the most popular language for adding, accessing and managing content in a database.

## API Documentation

Below is the list of endpoints for the To-Do List API:

| HTTP Method | Endpoint | Description | Request Body | Example Response |
|-------------|----------|-------------|--------------|------------------|
| GET | /todos | Retrieves all tasks | N/A | `[{"description":"Finishing all topics","is_done":true,"task_id":1,"title":"Learning docker"}]` |
| GET | /todos/<int:task_id> | Retrieves a task by ID | N/A | `{"description":"Finishing all topics","is_done":true,"task_id":1,"title":"Learning docker"}` |
| POST | /todos | Creates a new task | `{"title": "<title>", "description": "<description>"}` | `{"newly added task":{"description":"<description>","is_done":false,"task_id":2,"title":"<title>"}}` |
| PUT | /todos/<int:task_id> | Updates an existing task | `{"title": "<title>", "description": "<description>", "is_done": <bool>}` | `{"updated task":{"description":"<description>","is_done":<bool>,"task_id":2,"title":"<title>"}}` |
| DELETE | /todos/<int:task_id> | Deletes a task | N/A | `{"result":true}` |

Here, assume actual will come for each filed `<int:task_id>`, `<title>`, `<description>`, and `<bool>`. `<bool>` should be 0 for not done, and 1 for done.

This project can serve as a backend for any frontend service that needs to-do list functionality. Please make sure to update the `app.config` with your database credentials and other details.

Also, change api endpoint in html file.

