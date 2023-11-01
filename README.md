# Flask MongoDB Template API

This is a simple RESTful API built with Flask and MongoDB for managing templates.

## Prerequisites

- Python 3.x
- MongoDB
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account for hosting MongoDB (optional)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/flask-mongodb-template-api.git

2. Install the required Python packages using pip:

   ```bash
   pip install -r requirements.txt

3. Configuration

   In `constants.py`, you can configure your MongoDB connection details:

   ```python

    MONGODB_URL 
    MONGODB_DB 

## Postman Collection and Environment

I have included a Postman collection and environment for testing the API.

## Usage

Explain how to run and use the Flask application. Provide any important details about using your API, including how to start the server and what endpoints are available.

Example:

```markdown
4. Usage

   1. Run the Flask application:

      ```bash
      python app.py
      ```

   2. The API will be available at http://localhost:5000.

   3. API Endpoints

      - **Register**

        - **URL**: `/register`
        - **Method**: POST
        - **Headers**:
          - `Accept: application/json`
          - `Content-Type: application/json`
        - **Request Body**:
          ```json
          {
              "first_name": "John",
              "last_name": "Doe",
              "email": "john@example.com",
              "password": "password"
          }
          ```

      (Include details for other endpoints like Login, Template Operations, etc.)

