"""The TI radar interface is an interface for configuring and receiving data
from TI radars.
"""

import time
from abc import ABC, abstractmethod
from threading import Thread

from absl import logging

from radar.ti.ti_radar_config import (TiCliCommand, TiCliCommandString,
                                      TiRadarConfig)
from radar.ti.ti_radar_data_handler import TiRadarDataHandler
from utils.serial.serial_interface import SerialInterface

# TI radar UART baud rates.
TI_CONFIG_BAUDRATE = 115200
TI_DATA_BAUDRATE = 921600

# TI radar data read timeout in seconds.
TI_DATA_READ_TIMEOUT = 0.002  # seconds

# TI CLI start and stop guard time.
TI_CLI_START_STOP_GUARD_TIME = 0.1  # seconds


class TiRadarInterface:
    """Interface for configuring and receiving data from TI radars."""

    def __init__(self,
                 config_port: str,
                 data_port: str,
                 config_baudrate: int = TI_CONFIG_BAUDRATE,
                 data_baudrate: int = TI_DATA_BAUDRATE) -> None:
        self.config_serial = SerialInterface(config_port,
                                             config_baudrate,
                                             read_timeout=TI_DATA_READ_TIMEOUT,
                                             write_terminator=b"\n")
        self.data_serial = SerialInterface(data_port,
                                           data_baudrate,
                                           read_timeout=TI_DATA_READ_TIMEOUT)

        # Initialize the radar data handlers.
        self.config_handlers: list[TiRadarDataHandler] = []
        self.data_handlers: list[TiRadarDataHandler] = []

        # Create threads to listen for data from the radar.
        self.serial_threads = [
            Thread(target=self._read_data, args=(serial, handlers))
            for serial, handlers in ((self.config_serial, self.config_handlers),
                                     (self.data_serial, self.data_handlers))
        ]
        for thread in self.serial_threads:
            thread.start()

    def __del__(self):
        for thread in self.serial_threads:
            if thread.is_alive():
                thread.join()

    def add_config_handler(self, handler: TiRadarDataHandler) -> None:
        """Adds a radar data handler to the config port.

        Args:
            handler: Config data handler.
        """
        self.config_handlers.append(handler)

    def add_data_handler(self, handler: TiRadarDataHandler) -> None:
        """Adds a radar data handler to the config port.

        Args:
            handler: Data handler.
        """
        self.data_handlers.append(handler)

    def configure(self, config: TiRadarConfig) -> None:
        """Configures the radar.

        Args:
            config: TI radar config.
        """
        self.stop()
        for command in config.commands:
            self._send_command(command)

    def start(self, config: TiRadarConfig = None) -> None:
        """Starts the radar.

        Args:
            config: TI radar config. If provided, configures the radar prior to
              starting.
        """
        if config is not None:
            self.configure(config)
        command = TiCliCommand(TiCliCommandString.SENSOR_START)
        self._send_command(command)
        time.sleep(TI_CLI_START_STOP_GUARD_TIME)

    def stop(self) -> None:
        """Stops the radar."""
        command = TiCliCommand(TiCliCommandString.SENSOR_STOP)
        self._send_command(command)
        time.sleep(TI_CLI_START_STOP_GUARD_TIME)

    def _send_command(self, command: TiCliCommand) -> None:
        """Sends a command to the radar.

        Args:
            command: CLI command to send.
        """
        logging.info("> %s", command)
        self.config_serial.write(str(command).encode())

    @staticmethod
    def _read_data(serial: SerialInterface,
                   handlers: list[TiRadarDataHandler]) -> None:
        """Reads data from the serial port and forwards it to the radar data
        handlers.

        Args:
            serial: Serial interface.
            handlers: Radar data handlers.
        """
        while True:
            read_data = serial.read_all()
            if len(read_data) > 0:
                for handler in handlers:
                    handler.receive_data(read_data)
