from .types.get_pending_tasks_types import (
    GetPendingTasksUseCaseInput,
    GetPendingTasksUseCaseOutput,
)
from saviialib.libs.log_client import LogClient, LogClientArgs, LogStatus, DebugArgs
from .get_tasks import GetTasksUseCase, GetTasksUseCaseInput
from saviialib.services.tasks.presenters.task_notification_presenter import (
    TaskNotificationPresenter,
)
import re
from saviialib.libs.zero_dependency.utils.datetime_utils import (
    today,
    datetime_to_timestamp,
    str_to_datetime,
)
from saviialib.libs.email_client import SendEmailArgs


class GetPendingTasksUseCase:
    def __init__(self, input: GetPendingTasksUseCaseInput) -> None:
        self.logger = LogClient(
            LogClientArgs(service_name="tasks", class_name="get_pending_tasks")
        )
        self.presenter = TaskNotificationPresenter()
        self.notification_client = input.notification_client
        self.date_format = "%Y-%m-%d"
        self.today = datetime_to_timestamp(today(), self.date_format)
        self.email_client = input.email_client

    def _set_date_state(self, date_tmp: float):
        """If self.today > date_tmp, then the date_tmp is overdue (1). Otherwise, is on-time (0)"""
        return 1 if self.today > date_tmp else 0

    def _get_periodicity_params(self, periodicity: str) -> tuple[int, int]:
        """Extract and replace the daily, weekly, monthly, and anual strings into 4 categories
        (1, 2, 3, and 4). Additionaly, extract this category frequency."""
        periodicity_clean = (periodicity or "").strip().lower()

        if periodicity_clean == "sin periodicidad":
            return 0, 0

        frequency_match = re.search(r"cada\s+(\d+)", periodicity_clean)
        frequency = int(frequency_match.group(1)) if frequency_match else 0

        unit_mapping = {
            "día": 1,
            "dia": 1,
            "semana": 2,
            "mes": 3,
            "año": 4,
            "ano": 4,
        }
        unit = 0
        for unit_text, unit_code in unit_mapping.items():
            if unit_text in periodicity_clean:
                unit = unit_code
                break

        return frequency, unit

    def _preprocess_tasks(self, tasks: list) -> list:
        """Extract the needed attributes, and in the same time create the values to sort
        the array"""
        return list(
            map(
                lambda t: {
                    "title": t["title"],
                    "deadline": t["deadline"],
                    "priority": int(t["priority"]),
                    "assignee": t["assignee"],
                    "deadline_categ": self._set_date_state(
                        datetime_to_timestamp(
                            str_to_datetime(t["deadline"], self.date_format),
                            self.date_format,
                        )
                    ),
                    "periodicity_categ": self._get_periodicity_params(
                        t.get("periodicity", "")
                    )[0],
                    "periodicity_freq": self._get_periodicity_params(
                        t.get("periodicity", "")
                    )[1],
                },
                tasks,
            )
        )

    def _split_task_arrays(self, tasks: list) -> tuple[list, list]:
        """Split the sortered tasks in two arrays: overdue and on-time tasks"""
        return (
            list(
                map(
                    lambda t: {
                        "title": t["title"],
                        "deadline": t["deadline"],
                        "priority": t["priority"],
                        "assignee": t["assignee"],
                    },
                    filter(lambda t: t["deadline_categ"] == 1, tasks),
                )
            ),
            list(
                map(
                    lambda t: {
                        "title": t["title"],
                        "deadline": t["deadline"],
                        "priority": t["priority"],
                        "assignee": t["assignee"],
                    },
                    filter(lambda t: t["deadline_categ"] == 0, tasks),
                )
            ),
        )

    def _compare_by_attr(self, t: dict) -> tuple:
        return (
            -t["deadline_categ"],  # overdue(1) first
            -t["periodicity_categ"],  # anual(4) before daily(1)
            t["periodicity_freq"],  # each 1 before each 5
            -t["priority"],  # higher numeric priority first
        )

    async def _send_emails_to_assigned_users(self, tasks: list) -> None:
        # First we group by user and the tasks assigned to them
        user_tasks = {}
        for task in tasks:
            assignee_email = task.get("assignee_email")
            if not assignee_email:
                assignee = task.get("assignee")
                self.logger.debug(
                    DebugArgs(
                        LogStatus.EARLY_RETURN,
                        metadata={
                            "msg": (
                                f"Skipping email notification for {assignee}."
                                " Does not have an email address assigned."
                            )
                        },
                    )
                )
                continue
            if assignee_email not in user_tasks:
                user_tasks[assignee_email] = []
            user_tasks[assignee_email].append(task)
        # Then we send an email to each user with their assigned tasks
        for assignee_email, tasks in user_tasks.items():
            email_content = self.presenter.tasks_to_email(tasks)
            await self.email_client.send_email(
                SendEmailArgs(
                    recipient=assignee_email,
                    subject="[SAVIIA] Summary of your pending tasks",
                    body=email_content,
                    content_type="html",
                )
            )

    async def execute(self) -> GetPendingTasksUseCaseOutput:
        self.logger.method_name = "execute"
        self.logger.debug(DebugArgs(LogStatus.STARTED))

        uncompleted_tasks = await GetTasksUseCase(
            GetTasksUseCaseInput(
                self.notification_client,
                params={
                    "completed": False,
                    "fields": [
                        "title",
                        "deadline",
                        "priority",
                        "periodicity",
                        "assignee",
                        "assignee_email",
                        "description",
                    ],
                },
            )
        ).execute()

        preprocessed_tasks = self._preprocess_tasks(uncompleted_tasks.tasks)
        sorted_tasks = sorted(preprocessed_tasks, key=self._compare_by_attr)
        overdue, ontime = self._split_task_arrays(sorted_tasks)
        await self._send_emails_to_assigned_users(uncompleted_tasks.tasks)

        self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        return GetPendingTasksUseCaseOutput(overdue, ontime)
