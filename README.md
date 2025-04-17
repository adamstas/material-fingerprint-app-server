# MatTag Server

## Project Description

MatTag Server is a FastAPI server for material fingerprinting. The server supports a mobile application designed to create a visual identification of real-world materials by analyzing their visual attributes.

The system works with a machine learning model that predicts human evaluations of materials through a unified visual identifier - a vector of 16 visual attributes. This allows for the digital fingerprinting of physical materials, making it possible to compare, search, and filter materials based on their visual properties.

Key features of the whole system (mobile app + server) include:
- Processing material images to extract visual attribute vectors
- Storing material data both locally and on a remote server
- Visualizing material properties through polar graphs
- Searching for visually similar materials
- Filtering materials by adjusting vector values

This server provides the backend API for the Android mobile application, handling data storage, processing, and retrieval operations.

## Setup

Note: Ensure you run all commands in this README from the root folder of the server. Also, all commands are meant to be used on Linux.

Python version on which the server was tested and working is `3.10.15`.

You don't have to use a virtual environment, but it's recommended. Here's an example of how to set up using venv:

```bash
python -m venv fingerprintserver
source fingerprintserver/bin/activate
pip install -r requirements/requirements.txt
```

All dependencies should be installed from the `requirements/requirements.txt` file to ensure compatibility.

## How to Launch the Server

To launch the server in production mode, run the following command from the root folder of the project:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

This command:

* Uses uvicorn to serve the FastAPI application
* Loads the application from app/main.py (the app instance in that file)
* Binds to all network interfaces (0.0.0.0) making it accessible from other devices
* Runs on port 8000
* Creates 4 worker processes for handling concurrent requests


## Documentation

The complete API specification is available in the `docs/openapi.json` file. This is an OpenAPI 3.1 specification that can be:

- Viewed in any OpenAPI viewer
- Imported into API testing tools like Postman
- Used to generate client code in various languages
- Visualized online by uploading to Swagger Editor

Additionally, once the server is running, you can access the interactive API documentation at:

* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

## Tests

The server includes automated tests in the tests folder that verify all API routes and functionality.

To run tests, use command:

```bash
pytest tests/routers/materials.py
```

The tests should ensure all API endpoints function correctly. However, it is possible that not all use cases or edge cases have been tested.