FROM python:3.8

# Install python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Create a new directory named "myapp"
RUN mkdir /osmosis-validator-voting-comparison

# Set the working directory to the new directory
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