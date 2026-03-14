"""
Open Hollywood - AI Scene Execution Engine
Main entry point for the application.
"""

import logging
import argparse
from app.main import app
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Open Hollywood - AI Scene Execution Engine"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    logger.info(f"Starting Open Hollywood on {args.host}:{args.port}")
    logger.info("Make sure Ollama is running with gemma3:4b model")
    logger.info(f"Open http://{args.host}:{args.port} in your browser")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
