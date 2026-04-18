# 1. Start with a lightweight, official Python version
FROM python:3.12-slim

# 2. Tell Docker to work out of a folder named /app inside the container
WORKDIR /app

# 3. Copy the requirements file first and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy everything else in your folder (your scripts, database, and HTML)
COPY . .

# 5. Tell Docker the server uses port 8000
EXPOSE 8000

# 6. The command to start the app when the container turns on
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]