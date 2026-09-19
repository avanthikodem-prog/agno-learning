import logging
import os
import time

import requests
from dotenv import load_dotenv


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agentos_latency_test")


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

security_key = os.getenv("OS_SECURITY_KEY")

if not security_key:
    raise RuntimeError(
        "OS_SECURITY_KEY was not found in .env"
    )


# ============================================================
# AGENTOS REQUEST
# ============================================================

url = (
    "http://127.0.0.1:7777/"
    "agents/agri-assistant/runs"
)

headers = {
    "Authorization": f"Bearer {security_key}",
}

data = {
    "message": "What crops does Ravi grow?",
    "stream": "false",
}


# ============================================================
# MEASURE LATENCY
# ============================================================

logger.info(
    "Starting AgentOS latency test"
)

start_time = time.perf_counter()

response = requests.post(
    url,
    headers=headers,
    data=data,
    timeout=120,
)

elapsed = time.perf_counter() - start_time


# ============================================================
# RESULT
# ============================================================

logger.info(
    "AgentOS request completed"
)

print()
print("=" * 60)
print("AGENTOS LATENCY TEST")
print("=" * 60)

print(
    f"Status       : {response.status_code}"
)

print(
    f"Time         : {elapsed:.3f} seconds"
)

print(
    f"Response     : {response.text}"
)

print("=" * 60)