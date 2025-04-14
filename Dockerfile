# Use a Python base image
FROM python:3.12-slim

# Install necessary system libraries (libGL for OpenCV)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \  # This is the missing library for OpenCV
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies (make sure to use CPU-only TensorFlow here)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Set the default command to run your application
CMD ["python", "main.py"]
