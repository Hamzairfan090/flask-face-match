# Use a base Python image
FROM python:3.12-slim

# Install necessary system libraries (for OpenCV to work)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgthread-2.0-0 \  # Add missing dependency
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the default command to run your application
CMD ["python", "main.py"]
