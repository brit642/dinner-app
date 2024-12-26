# Use an official Python runtime as the base image
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port Flask will run on (default is 5000)
EXPOSE 5000

# Set the environment variable for Flask to run in production mode
ENV FLASK_ENV=production

# Run the Flask application using a production-ready WSGI server (Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]