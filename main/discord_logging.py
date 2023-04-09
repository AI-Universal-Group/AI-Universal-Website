"""
(c) 2023 Zach Lagden
This code is protected by copyright and can only be used for non-commercial purposes.
Any commercial use or reproduction in whole or part of this code without the expressed
written permission from the author is strictly prohibited.

The code provides a DiscordWebhookHandler class that enables logging to a Discord Webhook.
The handler takes `webhook_url`, `username` and `avatar_url` as arguments to send log records
to a specific webhook with appropriate colors assigned to the different log levels.
"""

import logging
from discord_webhook import DiscordWebhook, DiscordEmbed


class DiscordWebhookHandler(logging.Handler):
    """
    The DiscordWebhookHandler class extends the logging.Handler class.
    It sends log records to a Discord webhook.
    """

    def __init__(self, webhook_url, username=None, avatar_url=None):
        """
        Constructor method that initializes the DiscordWebhookHandler object.
        :param webhook_url: (str) URL of the Discord Webhook.
        :param username: (Optional[str]) Username of the sender. Default is None.
        :param avatar_url: (Optional[str]) URL of the sender's avatar. Default is None.
        """
        super().__init__()
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url

    def emit(self, record):
        """
        Overrides the emit method of the logging.Handler class.
        Creates an embed and sends it via Discord webhook based on the levelno of the log record.
        :param record: (LogRecord object) Record to be logged.
        """
        log_entry = self.format(record)
        if record.levelno >= logging.ERROR:
            color = 0xFF0000  # red
            title = "Error"
        elif record.levelno >= logging.WARNING:
            color = 0xFFA500  # orange
            title = "Warning"
        else:
            color = 0x008000  # green
            title = "Info"

        embed = DiscordEmbed(title=title, description=log_entry, color=color)
        if self.username:
            webhook = DiscordWebhook(
                url=self.webhook_url, username=self.username, avatar_url=self.avatar_url
            )
        else:
            webhook = DiscordWebhook(url=self.webhook_url)
        webhook.add_embed(embed)
        webhook.execute()


if __name__ == "__main__":
    # Example usage
    webhook_url = "https://discord.com/api/webhooks/1234567890/abcdefg"
    logger = logging.getLogger()
    logger.addHandler(
        DiscordWebhookHandler(
            webhook_url, username="Logger", avatar_url="https://example.com/logger.png"
        )
    )

    logger.info("This is an example info log message.")
    logger.warning("This is an example warning log message.")
    logger.error("This is an example error log message.")
