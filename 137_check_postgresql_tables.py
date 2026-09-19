import logging
import os

import psycopg
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("check_agentos_sessions")


def main():
    load_dotenv()

    database_url = os.getenv("POSTGRES_DB_URL")

    if not database_url:
        logger.error("POSTGRES_DB_URL is not configured")
        return

    logger.info("Connecting to PostgreSQL database")

    conn = psycopg.connect(database_url)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    session_id,
                    session_type,
                    created_at,
                    updated_at
                FROM ai.agno_sessions
                ORDER BY updated_at DESC
                LIMIT 10;
                """
            )

            sessions = cursor.fetchall()

            logger.info("PostgreSQL connection successful")
            logger.info("Found %d recent AgentOS sessions", len(sessions))

            print("\nRecent AgentOS sessions:\n")

            if not sessions:
                print("No sessions found.")

            for session in sessions:
                print(
                    f"Session ID: {session[0]}"
                )
                print(
                    f"Session Type: {session[1]}"
                )
                print(
                    f"Created: {session[2]}"
                )
                print(
                    f"Updated: {session[3]}"
                )
                print("-" * 60)

    finally:
        conn.close()
        logger.info("PostgreSQL connection closed")


if __name__ == "__main__":
    main()