import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
from logging.handlers import SysLogHandler
# Enable sending logs from the standard Python logging module to Sentry
logging_integration = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)
sentry_sdk.init(
    dsn="https://ee3ca659cdc5658bf02659af610f818b@o4507693153386496.ingest.de.sentry.io/4507693158629456",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    integrations= [logging_integration]
)

PAPERTRAIL_HOST = "logs6.papertrailapp.com"
PAPERTRAIL_PORT =  13596

handler = SysLogHandler(address=(PAPERTRAIL_HOST, PAPERTRAIL_PORT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[handler]
)

def get_logger(name):
    return logging.getLogger(name)

