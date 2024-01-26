# Builder stage
FROM python:3.9 as builder

# Set the working directory
WORKDIR /build

# Copy the Python project files first
COPY setup.py .
COPY requirements.txt .

# Install the project dependencies
RUN pip install --upgrade pip \
    && pip install --user -r requirements.txt

# Copy the rest of the project files
COPY . .

# Build/install the project
RUN pip install --user .

# Final stage
FROM python:3.9-slim

# Copy installed packages from the builder stage
COPY --from=builder /root/.local /root/.local

# Set the working directory
WORKDIR /searchengine

# Copy the application code
COPY . .

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["python","app.py"]


