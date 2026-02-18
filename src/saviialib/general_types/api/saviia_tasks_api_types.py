from dataclasses import dataclass


@dataclass
class SaviiaTasksConfig:
    """
    Configuration for SaviiaTasksConfig

    Attributes:
        bot_token (str): Notification Client Token for Tasks Channel creation
        task_channel_id (str): Channel ID at Notification Client application where the tasks are stored
    """

    bot_token: str = ""
    task_channel_id: str = ""
