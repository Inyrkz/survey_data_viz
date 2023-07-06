# Use the official Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .

# Expose the port your Flask API is running on (default is 5000)
EXPOSE 5000

# Define the command to run your Flask app
CMD ["python", "flask_api.py"]
