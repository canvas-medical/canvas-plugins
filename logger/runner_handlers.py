from django.conf import settings
from logstash_async.handler import AsynchronousLogstashHandler

from logger.logger import PluginLogger
from logger.logstash import LogstashFormatterECS
from logger.pubsub import PubSubLogHandler


def attach_runner_handlers(plugin_logger: PluginLogger) -> None:
    """Send the plugin logger's records to Redis pub/sub and Logstash, where configured.

    Redis pub/sub carries `canvas logs`, and Logstash carries the runner's logs to Elastic. The
    plugin runner calls this when it starts; the logger otherwise writes only to the console,
    so code that loads outside the runner needs neither package.
    """
    if settings.REDIS_ENDPOINT:
        plugin_logger.add_handler(PubSubLogHandler())

    if settings.LOGSTASH_HOST:
        plugin_logger.add_handler(
            AsynchronousLogstashHandler(
                host=settings.LOGSTASH_HOST,
                port=settings.LOGSTASH_PORT,
                database_path=None,
                transport=settings.LOGSTASH_PROTOCOL,
            ),
            LogstashFormatterECS(),
        )


__exports__ = ()
