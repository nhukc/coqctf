# Use the official Coq image as a parent image
FROM coqorg/coq:latest

# Switch to the root user to install packages
USER root

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./server /app

# Switch back to the default user (typically coq)
USER coq

# Make port 12345 available to the world outside this container
EXPOSE 12345

# Run server.py when the container launches
CMD ["python3", "server.py"]

