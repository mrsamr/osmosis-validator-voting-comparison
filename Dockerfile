FROM python:3.11-slim

# Install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /osmosis-validator-voting-comparison

# Copy source code files
COPY app.py app.py
COPY src src
COPY static static
COPY tests tests
COPY .streamlit .streamlit

# Create data directory
RUN mkdir data
RUN mkdir credentials

CMD ["streamlit", "run", "app.py"]