# Assignment 1: Two Provider Cost Tracker

## Overview

This Python project sends the same prompt to two LLM providers:
Google Gemini and Groq.

It displays the response from each provider, actual input and
output token counts, execution time, and estimated API cost.

The results are also saved in a JSON file.

## Technologies Used

- Python 3.12+
- uv (Python package manager)
- Google Gemini API
- Groq API
- python-dotenv

## Setup Instructions

### 1. Clone the repository

git clone https:\\Repo-URL
cd folder-name

### 2. Install dependencies

uv sync

### 3. Configure API keys

Copy .env.example to .env and replace the placeholder keys with
our own Gemini and Groq API keys.

Required environment variables:

- GEMINI_API_KEY
- GROQ_API_KEY
- GEMINI_MODEL
- GROQ_MODEL

### 4. Run the program

uv run tracker.py "What is an AI agent?"

## Sample Output

The program prints the reply from each model, followed by a
comparison table.

| Provider | Input | Output | Seconds | Cost (USD) |
| -------- | ----: | -----: | ------: | ---------: |
| gemini   |    11 |     24 |   2.124 | 0.00006330 |
| groq     |    81 |     63 |   0.573 | 0.00002498 |

These values are from a sample successful execution.

## Cost Calculation

Cost = (input_tokens * input_price_per_m / 1,000,000) + (output_tokens * output_price_per_m / 1,000,000)

Prices are expressed in USD per million tokens.

## Output File

The script creates results.json containing a list of two
objects, one for each provider.

Each object includes:

- provider
- model
- reply
- input_tokens
- output_tokens
- input_price_per_m
- output_price_per_m
- cost_usd

## Testing

The script was tested using three different prompts:

1. What is an AI agent? Answer in one sentence.
2. List three benefits of Python programming.
3. Explain the difference between a Python list and tuple in two sentences.

## Key Learning

I learnt how to connect Python to multiple LLM providers
using their APIs and retrieve actual token usage instead of
estimating it.

## Security

API keys are stored locally in .env, which is excluded from
Git using .gitignore. The repository includes .env.example
with placeholder values only.
