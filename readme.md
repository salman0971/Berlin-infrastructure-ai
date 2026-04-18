# Berlin Infrastructure AI: Natural Language to SQL 

A containerized AI-powered data intelligence platform that turns natural language into verified, geospatial database queries. 

## Overview
This microservice bypasses the traditional GIS bottleneck. It allows users to query complex urban infrastructure databases in plain English. The system resolves user intent, maps it to a strict data dictionary, generates validated SQLite queries, and renders the results on a reactive, open-source GIS dashboard.

## Technical Architecture
* **Backend:** Python / FastAPI
* **LLM Orchestration:** Anthropic Claude for NL-to-SQL translation
* **Database:** SQLite (Relational mapping of unstructured JSON Open Data)
* **Frontend:** Vanilla JS, Tailwind CSS, Leaflet.js
* **Infrastructure:** Fully containerized via Docker

## Key Engineering Features
1. **Semantic Intent & Data Dictionary Routing:** The LLM is injected with a strict data dictionary schema. It successfully translates colloquial English ("Show me severe closures") into strict German database entries (`WHERE severity = 'vollsperrung'`), eliminating hallucinated SQL parameters.
2. **Dynamic GIS Rendering:** The frontend intercepts database coordinates and utilizes the OpenStreetMap API to dynamically fetch and draw polygon boundaries (e.g., highlighting a specific district) based purely on the AI's SQL output.
3. **Reactive UI State:** The map legend dynamically generates itself based on the database response, converting raw German database strings into an interactive, case-insensitive English filtering system.

## How to Run Locally

### 1. Setup your Environment
1. Clone this repository.
2. Create a file named `.env` in the root directory.
3. Add your Anthropic API key to the file like this:
   `CLAUDE_API_KEY=your_api_key_here`

### 2. Run via Docker (Recommended)
Ensure Docker is installed and running on your machine.
```bash
# Build the image
docker build -t berlin-infrastructure-ai .

# Run the container
docker run -p 8000:8000 --env-file .env berlin-infrastructure-ai