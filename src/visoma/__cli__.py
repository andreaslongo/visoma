import fire
import logging
import sys

from visoma import VisomaClient

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.WARNING)

    try:
        with VisomaClient.from_env() as client:
            fire.Fire(client)
    except Exception as e:
        log.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
