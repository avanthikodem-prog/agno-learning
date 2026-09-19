import logging
import time

import requests


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("ollama_timing_test")


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2"


def run_test():
    logger.info("Starting direct Ollama timing test")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "What crops does Ravi grow?",
            }
        ],
        "stream": False,
    }

    start = time.perf_counter()

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    total_time = time.perf_counter() - start
    data = response.json()

    load_time = data.get("load_duration", 0) / 1e9
    prompt_time = data.get("prompt_eval_duration", 0) / 1e9
    generation_time = data.get("eval_duration", 0) / 1e9

    print("\n" + "=" * 60)
    print("DIRECT OLLAMA TIMING TEST")
    print("=" * 60)
    print(f"Model       : {MODEL}")
    print(f"Total       : {total_time:.3f} seconds")
    print(f"Load        : {load_time:.3f} seconds")
    print(f"Prompt      : {prompt_time:.3f} seconds")
    print(f"Generation  : {generation_time:.3f} seconds")
    print(f"Response    : {data['message']['content']}")
    print("=" * 60)

    logger.info("Direct Ollama timing test completed")


if __name__ == "__main__":
    run_test()