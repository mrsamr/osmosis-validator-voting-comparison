Osmosis: Validator Voting Comparison
===================================

[![Build](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/build.yml/badge.svg)](https://github.com/mrsamr/osmosis-validator-voting-comparison/actions/workflows/build.yml)


A simple app that enables a user to compare multiple Osmosis validators based on their voting history.

---

Overview
--------

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

---

Usage and Deployment
--------------------

#### Running the app locally

Run the following command.

```sh
streamlit run app.py
```

#### Running the app via Docker

Build the image.
```
docker build --tag osmo-validator-voting .
```

Create container and run the app.
```
docker run -p 8051:8051 osmo-validator-voting
```

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
├── sql                <- Data extraction SQL statements (for reference only)
├── static             <- Static assets and files, e.g. CSS, txt, etc.
└── utils              <- Data extraction and processing functions
```
