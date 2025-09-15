# AIS Umbrella pipeline


This repository demonstrates an end-to-end data pipeline for processing AIS (Automatic Identification System) messages from ships at sea. The pipeline moves streaming and metadata through an ETL (Extract-Transform-Load) process into a database, enabling users to query the data via an API.
Note: This is a demo project, not a production-ready system. The purpose is to showcase architectural thinking and the construction of full pipelines, rather than focusing on individual services.

# How to Run the Project

To start all services:

./deployment.sh --function start_all_services
You can also test the querying functionality after the pipeline is running:


# What the Pipeline Does

Running ./deployment.sh will:
1. Set up the asi-db database container
    * Initializes schema based on provided metadata
    * Creates tables for both metadata and streaming data
2. Deploy Kafka, Zookeeper, and AKHQ containers
    * Used for managing and inspecting Kafka topics
3. Connect all containers via a custom Docker network (asi_network)
4. Start the pipeline, which includes:
    * meta_ingestion: Loads metadata into the database
    * data_puller: Streams AIS data into Kafka topics
    * data_writer: Consumes Kafka data and writes to the database
    * asi-api: Exposes a REST API at localhost:5000 for querying the data
5. Inspect Kafka topics via AKHQ at: http://localhost:8080

# Project structure

### 🗂️ Root Directory Structure

| File/Folder       | Description                                                                                     |
|-------------------|-------------------------------------------------------------------------------------------------|
| `asi-db`          | Database schema (`schema.sql`) and container definition (`.yaml`)                              |
| `docs`            | Architecture diagrams and parameter documentation for metadata and streaming                   |
| `kafka_build`     | Docker Compose config for Kafka, Zookeeper, AKHQ (exposed ports: 9092/29092)                   |
| `pipeline`        | Pipeline source code (detailed in a separate section below)                                    |
| `deployment.sh`   | Script to deploy the full stack                                                                |
| `query_data.sh`   | Script to query the API and test data retrieval                                                |


# Pipeline architecture 

The pipeline is built as a monorepo for development convenience. In production, each service should ideally be its own Docker image.


### 🗂️ `pipeline/` Directory Structure

| File/Folder                | Description                                                                                             |
|----------------------------|---------------------------------------------------------------------------------------------------------|
| `data/`                    | Streaming data pushed into Kafka and later written into the database                                    |
| `metadata/`                | Metadata ingested into the database via the `meta_ingestion` service                                    |
| `src/`                     | Source code for the ETL pipeline                                                                        |
| `tests/`                   | Local test script (assumes the database is running with ingested data)                                 |
| `configuration.yaml`       | Local development configuration: toggles modules and localhost vs Docker network                        |
| `configuration_compose.yaml` | Compose-specific configuration injected into the container as a volume                                |
| `docker-compose.yaml`      | Docker Compose file for the pipeline services                                                           |
| `Dockerfile`               | Multi-stage Dockerfile for building pipeline image with minimal size                                    |
| `lint.sh`                  | Lint script using Poetry                                                                                 |


1. src/pipeline/dependencies/

These are shared modules uded across the pipeline services

### 🧩 Pipeline Dependencies

| Module             | Description                                                                                              |
|--------------------|----------------------------------------------------------------------------------------------------------|
| `base_app`         | Provides shared application logic, such as a base runner and a common logger used across all pipeline pods |
| `decoder`          | Contains logic for decoding Kafka messages and mapping message types to models and database tables        |
| `driver`           | Database interaction layer with async connection pooling and SQL query building/validation utilities       |
| `models`           | Centralized Pydantic models used for validating both metadata and streaming data                          |
| `data_process`     | (Optional) Utility functions that support data transformation and processing                              |
                                 |

2. src/pipeline/pods/

these are individual pipeline services ("pods") that could become separate microservices

### 📦 Pipeline Pods

| Pod Name        | Description                                                                                  |
|-----------------|----------------------------------------------------------------------------------------------|
| `meta_ingestion`| Loads metadata from CSV files into the database using Pydantic validation                    |
| `data_puller`   | Reads data from local files and streams it to Kafka topics                                   |
| `data_writer`   | Consumes Kafka messages and writes them to the corresponding DB tables                       |
| `asi_api`       | REST API that exposes the query interface on [localhost:5000](http://localhost:5000)         |

 
## 🔌 Dependencies Breakdown

The `src/pipeline/dependencies/` directory contains shared modules used across the ETL pipeline services.

---

### 📦 `base_app`

- Unified application structure used by all pods  
- Includes:
  - A common logger  
  - A base runner for executing services

---

### 📦 `decoder`

- Standardized decoding of Kafka messages across all pods  
- Maps message types (e.g., `vessel`, `voyage`, `sar`) to:
  - Corresponding Pydantic model  
  - Target database table

> **Note:** The message-to-table mapping logic could ideally be moved into the `data_writer` pod for better cohesion.

---

### 📦 `driver`

- Core database interaction layer  
- Key methods:
  - `insert_meta_data()`
  - `insert_streaming_data()`
  - `query_data()`
- Includes:
  - Async connection pooling
  - Query builder with validation
  - Table metadata information for dynamic SQL generation

---

### 📦 `models`

- Centralized data validation using Pydantic models  
- Divided into:
  - `meta_models.py`: For static metadata (used by `meta_ingestion`)  
  - `wire_models.py`: For dynamic/streaming data (used by `data_writer`, etc.)

---


# Example Use Case
After starting all services:
1. Access AKHQ to inspect Kafka topics: → http://localhost:8080
2. Call the API on localhost:5000 using curl or the provided query_data.sh:

./query_data.sh
1. Try modifying the queries — or break things! The system is made to be explored and stress-tested.

 # 🏁Final Notes
* This demo is structured to provide a complete view of an ETL pipeline architecture using Docker, Kafka, PostgreSQL, and FastAPI.
* It is intentionally structured as a monolith for development simplicity, but real-world deployments should separate pods into independent services/images.


