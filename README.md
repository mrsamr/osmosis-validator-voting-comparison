Osmosis: Validator Voting Comparison
===================================

[![Build](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/build.yml/badge.svg)](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/build.yml)
[![Unit Tests](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/unit_tests.yml)
[![Integration Tests](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/integration_tests.yml)
[![Data Quality Tests](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/data_quality_tests.yml/badge.svg)](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/data_quality_tests.yml)
[![Data Refresh](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/scheduled_data_refresh.yml/badge.svg)](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/scheduled_data_refresh.yml)


A simple app that enables a user to compare multiple Osmosis validators based on their voting history.

Check out the live app [here](https://osmosis-validator-voting-comparison-mrsamr.streamlit.app/). 

---

Overview
--------

This project is a Streamlit app that displays information on the voting history of Osmosis validators. Data is sourced
from Atomscan and Flipside Crypto. This project is comprised of two main parts:

1. **Data pipeline.** A batch ETL job that extracts data from Atomscan and Flipside crypto. Data is formatted
and then stored in a Google Cloud Storage bucket. This job is orchestrated via Github actions on a schedule, 
e.g. every 12 hours. The purpose of this batch job is to cache the data for faster response times on the main web app.
1. **Streamlit web app.** This is the front-end web app which enables users to explore the data. This is hosted
on Streamlit cloud and can be accessed [here](https://osmosis-validator-voting-comparison-mrsamr.streamlit.app/).

This project was built by [rmas](https://twitter.com/rmas_11) as an open-source contribution to [MetricsDAO](https://metricsdao.xyz) and to the community in general. Please reach out on Twitter if you have any questions or if you would like to collaborate.

---

Development
-----------
For development purposes, it is recommended to have the following setup:

1. Mac or Linux machine
1. Miniconda

#### Environment Setup

Clone the repository.

```sh
git clone https://github.com/mrsamr/osmosis-validator-voting-comparison.git;
cd osmosis-validator-voting-comparison
```

Install python and packages.

```sh
conda create -n streamlit python==3.8;
conda activate streamlit;
pip install -r requirements.txt;
```

#### Data Initialization

Before running the app, you need to cache the datasets first on a Google Cloud Storage bucket.

1. Prepare your Google Cloud service account key and store it as:
   - `credentials/service_account_key.json`

1. Set the bucket name environment variable:
   - `export GCS_BUCKET=<YOUR_BUCKET_NAME>`
   
1. Set the Flipside API key environment variable:
   - `export FLIPSIDE_API_KEY=<YOUR_API_KEY>`

1. Run the data pipeline:
   - `python -m src.etl.refresh_datasets`
    
1. Start the app:
   - `streamlit run app.py`

#### Testing

Run unit tests:

```sh
pytest tests/unit
```

Run integration tests:

```sh
pytest tests/integration
```

Run data quality checks:

```sh
pytest tests/data
```

---

Usage and Deployment
--------------------

#### Running locally

Run the data pipeline.
```sh
export GCS_BUCKET=<YOUR_BUCKET_NAME>;
export FLIPSIDE_API_KEY=<YOUR_API_KEY>;
python -m src.etl.refresh_datasets
```

Start the app.
```sh
export GCS_BUCKET=<YOUR_BUCKET_NAME>;
streamlit run app.py
```

Open the app at `http://localhost:8501`.


#### Running via Docker

Build the image.
```
docker build --tag osmo-validator-voting .
```

Run the data pipeline.
```sh
docker run \
  -v $PWD/credentials:/osmosis-validator-voting-comparison/credentials
  -e GCS_BUCKET=<YOUR_BUCKET_NAME> \
  -e FLIPSIDE_API_KEY=<YOUR_API_KEY> \
  python -m src.etl.refresh_datasets
```

Start the app.
```sh
docker run \
  -e GCS_BUCKET=<YOUR_BUCKET_NAME> \
  -p 8501:8501 \
  osmo-validator-voting
```

Open the app at `http://localhost:8501`.

#### Deploying on Streamlit Cloud

Follow the official instructions in the Streamlit [docs](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app).

---

Project Organization
--------------------

```
├── app.py             <- The main application code
├── LICENSE            <- Contains the software license used by this project
├── README.md          <- The top-level README for developers using this project
├── requirements.txt   <- The requirements file for reproducing the python environment
│
├── src                <- Contains source code files
│   ├── etl            <- Data pipeline code
│   ├── sql            <- Data extraction SQL statements
│   └── utils          <- Data extraction and processing functions
│
├── static             <- Static assets and files, e.g. CSS, txt, etc.
└── tests              <- Test scripts
```
