import logging

format_log = "#%(levelname)-8s [%(asctime)s] - %(filename)s:%(lineno)d - %(name)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=format_log,
)
log = logging.getLogger(__name__)
