
import os
import sys
import time
import json

from dotenv import load_dotenv
from google import genai
from groq import Groq

# Load API keys and settings from .env
load_dotenv()

# Standard paid prices in USD per 1 million tokens
MODEL_PRICES = {
    "gemini-3.5-flash-lite": {
        "input": 0.30,
        "output": 2.50,
    },
    "openai/gpt-oss-20b": {
        "input": 0.075,
        "output": 0.30,
    },
}


def call_gemini(prompt: str) -> dict:
    """Send a prompt to Gemini and return its response and usage."""

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    client = genai.Client(api_key=api_key)

    
    
    print("Connecting to Gemini...", flush=True)

    start = time.perf_counter()

    print(f"Sending request to model: {model}", flush=True)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    print("Gemini response received!", flush=True)


    seconds = time.perf_counter() - start
    usage = response.usage_metadata

    if usage is None:
        raise RuntimeError("Gemini returned no token usage data")

    return {
        "provider": "gemini",
        "model": model,
        "reply": response.text,
        "input_tokens": usage.prompt_token_count,
        "output_tokens": (
    (usage.candidates_token_count or 0)
    + (usage.thoughts_token_count or 0)
),
        "thinking_tokens": usage.thoughts_token_count or 0,
        "seconds": round(seconds, 3),
    }


def call_groq(prompt: str) -> dict:
    """Send a prompt to Groq and return the reply and token usage."""

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    client = Groq(api_key=api_key, timeout=30.0)

    print("Connecting to Groq...", flush=True)

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    seconds = time.perf_counter() - start
    usage = response.usage

    if usage is None:
        raise RuntimeError("Groq returned no token usage data")

    return {
        "provider": "groq",
        "model": model,
        "reply": response.choices[0].message.content,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "seconds": round(seconds, 3),
    }


def add_cost(result: dict) -> dict:
    """Calculate the estimated paid-tier cost of an API call."""

    model = result["model"]

    if model not in MODEL_PRICES:
        raise ValueError(f"No pricing configured for model: {model}")

    prices = MODEL_PRICES[model]

    input_tokens = result["input_tokens"]
    output_tokens = result["output_tokens"]
    thinking_tokens = result.get("thinking_tokens", 0)

    input_price = prices["input"]
    output_price = prices["output"]

    input_cost = input_tokens * input_price / 1_000_000

    output_cost = output_tokens * output_price / 1_000_000

    total_cost = input_cost + output_cost

    result["input_price_per_m"] = input_price
    result["output_price_per_m"] = output_price
    result["cost_usd"] = round(total_cost, 10)

    return result



def main():
    """Run both providers and compare their costs."""

    prompt = " ".join(sys.argv[1:]).strip()

    if not prompt:
        print('Usage: uv run tracker.py "Your prompt"')
        return 1

    results = []

    # Send the SAME prompt to both providers
    for call_function in [call_gemini, call_groq]:
        try:
            result = call_function(prompt)
            result = add_cost(result)
            results.append(result)

        except Exception as error:
            print(
                f"Error calling {call_function.__name__}: {error}"
            )
            return 1

    # Print both replies
    for result in results:
        print(f"\n{'=' * 55}")
        print(f"Provider: {result['provider'].upper()}")
        print(f"Model: {result['model']}")
        print(f"Reply:\n{result['reply']}")

    # Print comparison table
    print("\n" + "=" * 76)
    print("TWO PROVIDER COST COMPARISON")
    print("=" * 76)

    header = (
        f"{'Provider':<12}"
        f"{'Input':>10}"
        f"{'Output':>10}"
        f"{'Seconds':>12}"
        f"{'Cost (USD)':>18}"
    )
    print(header)
    print("-" * 76)

    for result in results:
        print(
            f"{result['provider']:<12}"
            f"{result['input_tokens']:>10}"
            f"{result['output_tokens']:>10}"
            f"{result['seconds']:>12.3f}"
            f"${result['cost_usd']:>17.8f}"
        )

    # Save exactly the fields requested in the PDF
    required_fields = [
        "provider",
        "model",
        "reply",
        "input_tokens",
        "output_tokens",
        "input_price_per_m",
        "output_price_per_m",
        "cost_usd",
    ]

    saved_results = [
        {field: result[field] for field in required_fields}
        for result in results
    ]

    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(saved_results, file, indent=2, ensure_ascii=False)

    print("\nResults saved to results.json")
    print("Costs are estimated paid-tier equivalents.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
