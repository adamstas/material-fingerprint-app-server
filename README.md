# MatTag Server

## Project Description

MatTag Server is a FastAPI server for material fingerprinting. The server supports a mobile application designed to create a visual identification of real-world materials by analyzing their visual attributes.

The mobile app is fully described including its source code in its GitHub repository:  
[material-fingerprint-app](https://github.com/adamstas/material-fingerprint-app)

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

## HTTPS Setup for Android App

**Important:** To connect the server to the MatTag Android app, it **must run over HTTPS** with a valid SSL certificate. Without HTTPS, the app will not connect.

## How to Launch the Server

Firstly it is needed to obtain an SSL certificate. In this README the free SSL certificate via Let’s Encrypt will be used.

### Obtain a free SSL certificate via Let’s Encrypt

```bash
sudo apt update
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

This will generate the certificate files:

- `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- `/etc/letsencrypt/live/yourdomain.com/privkey.pem`

### Launch the Server with HTTPS

To launch the server in production mode, run the following command from the root folder of the project:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 443 \
    --ssl-keyfile /etc/letsencrypt/live/yourdomain.com/privkey.pem \
    --ssl-certfile /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
    --workers 4
```

This command:

* Uses uvicorn to serve the FastAPI application
* Loads the application from app/main.py (the app instance in that file)
* Binds to all network interfaces (0.0.0.0) making it accessible from other devices
* Runs on port 443 which means that in MatTag app no port has to be specified
* Creates 4 worker processes for handling concurrent requests

Now your server is accessible at https://yourdomain.com and the Android app can connect securely.

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
pytest tests/routers/test_materials.py
```

The tests should ensure all API endpoints function correctly. However, it is possible that not all use cases or edge cases have been tested.

## Acknowledgements

This software was created with the support of the Faculty of Information Technology, Czech Technical University in Prague (FIT CTU) – www.fit.cvut.cz

![FIT CTU logo](fit_logo.jpg)

It was also developed with the support of the **Institute of Information Theory and Automation of the CAS (UTIA)**, public research institution – www.utia.cas.cz

![UTIA logo](utia_logo.png)