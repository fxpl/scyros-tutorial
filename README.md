# Tutorial: Getting Started with Scyros

[![Actions status](https://github.com/fxpl/scyros-tutorial/actions/workflows/docker.yml/badge.svg)](https://github.com/fxpl/scyros-tutorial/actions)
![License](https://img.shields.io/crates/l/scyros.svg)
[![GitHub release](https://img.shields.io/github/v/release/fxpl/scyros)](https://github.com/fxpl/scyros/releases)

This repository contains an interactive tutorial showing how to use Scyros to mine GitHub repositories and extract functions from real-world code. In the tutorial, we build a small end-to-end pipeline to extract functions with integer types in C and Java repositories mined from GitHub. 

The tutorial itself runs inside a Streamlit web application.
The purpose of this README is only to help you set up and launch the tutorial environment. Once the application is running, open it in your browser and follow the step-by-step instructions provided in the interface.


## Installation instructions

First clone the repository to your local machine:

```bash
git clone git@github.com:fxpl/scyros-tutorial.git
cd scyros-tutorial
```

After cloning the repository, choose one of the installation methods below.

### Using Docker (recommended)

To build the Docker image, please follow the steps below:
1. Ensure Docker is installed: https://www.docker.com/get-started.
2. Open a terminal and navigate to the directory containing this `README.md` file and the `Dockerfile`.
3. Build the Docker image using the following command:
    ```bash
    docker build -t scyros-tutorial .
    ``` 
4. After completion, verify that the image has been created successfully by running:
    ```bash
    docker images
    ```
   You should see `scyros-tutorial` listed.

5. Start the container. This should not take more than a minute.
    ```bash
    docker run --rm -p 8501:8501 scyros-tutorial:latest 
    ```

6. Click on the link displayed in the terminal (`http://localhost:8501`) or, alternatively, open [http://localhost:8501](http://localhost:8501) in your browser.
    
7. While the container is running, you can open a terminal inside the container to run commands and inspect the file system. Fetch first the container by ID running
`docker ps` in a new terminal on your host, and then:
    ```bash
    docker exec -it <container-id> /bin/bash  
    ```

### Local installation


1. Make sure you have [scyros](https://github.com/fxpl/scyros) installed on your machine. In most cases, you can install it using the following command:
    ```bash
    curl --proto '=https' --tlsv1.2 -LsSf https://github.com/fxpl/scyros/releases/latest/download/scyros-installer.sh | sh
    ```
    For more information on available releases and installation options, please refer to the [release page of the Scyros repository](https://github.com/fxpl/scyros/releases).
2. Make sure you have [uv](https://github.com/astral-sh/uv) installed on your machine. You can install it using the following command:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
3. uv installs to ~/.local/bin by default; make sure to add this directory to your PATH environment variable if it's not already included.
4. Run the following commands to set up the virtual environment and install the dependencies (you may need to run these commands as a superuser):
    ```bash 
    uv python install
    uv venv 
    source .venv/bin/activate
    uv sync
    ```
5. Start the Streamlit application:
    ```bash
    uv run streamlit run Scyros_Tutorial.py
    ```


## Clean-up

To remove the Docker image and free up disk space, you can run the following command in the host terminal:
```bash
docker rmi scyros-tutorial:latest
```
Remember to revoke your GitHub personal access token in your GitHub account settings.

## Troubleshooting

- If `docker run` fails with an error similar to the one below, it means that port 8501 is already in use on your machine.
    ````
    docker: Error response from daemon: ports are not available: exposing port TCP 0.0.0.0:8501 -> 127.0.0.1:0: listen tcp 0.0.0.0:8501: bind: address already in use.
    ````
    To solve this, you can either stop the process using that port, or run the container mapping to a different port (e.g., 8502):
    ```bash
    docker run --rm -p 8502:8501 scyros-tutorial:latest 
    ```
    The application will be accessible at: [http://localhost:8502](http://localhost:8502)
   
