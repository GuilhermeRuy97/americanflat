FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./

# Install poetry
RUN pip install poetry

# Copy project files
COPY . .

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["python", "main.py"] 