"""HORIZON Device Agent - Main entry point."""
import argparse
import logging
import sys
import time
from pathlib import Path

from agent.config import load_config
from agent.heartbeat import HeartbeatSender
from agent.telemetry import TelemetrySender


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main():
    """Main agent loop."""
    parser = argparse.ArgumentParser(description="HORIZON Device Agent")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("horizon-agent.yaml"),
        help="Path to configuration file",
    )
    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Setup logging
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    logger = logging.getLogger(__name__)

    logger.info("HORIZON Device Agent starting...")

    # Initialize senders
    heartbeat_sender = HeartbeatSender(config)
    telemetry_sender = TelemetrySender(config)

    logger.info(f"Server: {config['server']['url']}")
    logger.info(f"Heartbeat interval: {config['heartbeat']['interval_seconds']}s")
    logger.info(f"Telemetry enabled: {config['telemetry']['enabled']}")

    # Main loop
    last_heartbeat = 0
    last_telemetry = 0

    try:
        while True:
            current_time = time.time()

            # Send heartbeat
            if current_time - last_heartbeat >= config["heartbeat"]["interval_seconds"]:
                try:
                    heartbeat_sender.send_heartbeat()
                    last_heartbeat = current_time
                except Exception as e:
                    logger.error(f"Failed to send heartbeat: {e}")

            # Send telemetry
            if config["telemetry"]["enabled"]:
                if current_time - last_telemetry >= config["telemetry"]["interval_seconds"]:
                    try:
                        telemetry_sender.send_telemetry()
                        last_telemetry = current_time
                    except Exception as e:
                        logger.error(f"Failed to send telemetry: {e}")

            # Sleep for 10 seconds between checks
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Agent error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
