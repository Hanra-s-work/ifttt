"""_summary_
    File in charge of containing the functions that will be run in the background.
"""
from typing import Union, Dict, Any
from datetime import datetime
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .runtime_data import RuntimeData
from . import constants as CONST


class Crons:
    """_summary_
    """

    def __init__(self, runtime_data: RuntimeData, error: int = 84, success: int = 0, debug: bool = False) -> None:

        # -------------------------- Inherited values --------------------------
        self.error: int = error
        self.success: int = success
        self.debug: bool = debug
        self.runtime_data: RuntimeData = runtime_data
        # ---------------------- The visual logger class  ----------------------
        self.disp: Disp = Disp(
            TOML_CONF,
            SAVE_TO_FILE,
            FILE_NAME,
            FILE_DESCRIPTOR,
            debug=self.debug,
            logger=self.__class__.__name__
        )

    def inject_crons(self) -> int:
        """_summary_
            Add the cron functions to the cron loop.

        Returns:
            int: _description_: The overall status of the injection.
        """
        self.runtime_data.background_tasks_initialised.safe_add_task(
            func=self.check_actions,
            args=None,
            trigger='interval',
            seconds=CONST.CHECK_ACTIONS_INTERVAL
        )
        if CONST.ENABLE_TEST_CRONS is True:
            test_delay = 200
            self.runtime_data.background_tasks_initialised.safe_add_task(
                func=self._test_current_date,
                args=datetime.now,
                trigger='interval',
                seconds=test_delay
            )
            self.runtime_data.background_tasks_initialised.safe_add_task(
                func=self._test_hello_world,
                args=None,
                trigger='interval',
                seconds=test_delay
            )
        if CONST.CLEAN_TOKENS is True:
            self.runtime_data.background_tasks_initialised.safe_add_task(
                func=self.clean_expired_tokens,
                args=None,
                trigger='interval',
                seconds=CONST.CLEAN_TOKENS_DELAY
            )

    def _test_hello_world(self) -> None:
        """_summary_
            This is a test function that will print "Hello World".
        """
        self.disp.log_info("Hello World", "_test_hello_world")

    def _test_current_date(self, *args: Any) -> None:
        """_summary_
            This is a test function that will print the current date.
        Args:
            date (datetime): _description_
        """
        if len(args) >= 1:
            date = args[0]
        else:
            date = datetime.now()
        if callable(date) is True:
            self.disp.log_info(
                f"(Called) Current date: {date()}",
                "_test_current_date"
            )
        else:
            self.disp.log_info(
                f"(Not called) Current date: {date}",
                "_test_current_date"
            )

    def clean_expired_tokens(self) -> None:
        """_summary_
            Remove the tokens that have passed their lifespan.
        """
        title = "clean_expired_tokens"
        date_node = "expiration_date"
        current_time = datetime.now()
        self.disp.log_info("Cleaning expired tokens", title)
        current_tokens = self.runtime_data.database_link.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="*",
            where="",
            beautify=True
        )
        self.disp.log_debug(f"current tokens = {current_tokens}", title)
        for i in current_tokens:
            if i[date_node] is not None and i[date_node] != "" and isinstance(i[date_node], str) is True:
                datetime_node = self.runtime_data.database_link.string_to_datetime(
                    i[date_node]
                )
                msg = f"Converted {i[date_node]} to a datetime instance"
                msg += f" ({datetime_node})."
                self.disp.log_debug(msg, title)
            else:
                datetime_node = i[date_node]
                self.disp.log_debug(f"Did not convert {i[date_node]}.", title)
            if datetime_node < current_time:
                self.runtime_data.database_link.remove_data_from_table(
                    table=CONST.TAB_CONNECTIONS,
                    where=f"id='{i['id']}'"
                )
                self.disp.log_debug(f"Removed {i}.", title)
        self.disp.log_debug("Cleaned expired tokens", title)

    def check_actions(self) -> None:
        """_summary_
            Function in charge of checking if any actions need to be run.
        """
        title = "check_actions"
        self.disp.log_debug("Checking for actions that need to be run.", title)
        self.disp.log_critical("Implement action checking", title)
        self.disp.log_debug("Checked for actions that needed to be run", title)
