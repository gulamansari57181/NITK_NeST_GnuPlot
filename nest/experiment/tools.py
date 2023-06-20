# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Check if tool is installed and tool options are valid"""

from nest.engine.util import is_dependency_installed, is_package_installed
from nest.input_validator import input_validator


# pylint: disable=too-few-public-methods, invalid-name, missing-class-docstring
class Tools:
    """
    Check that the tool is available.
    """

    @input_validator
    def __init__(self, tool_name: str):
        """
        Parameters
        ----------
        tool_name: str
            name of tool

        """

        self.tool_name = tool_name

        if (self.tool_name == "coap") and not is_package_installed("aiocoap"):
            raise ValueError("coap is not installed.")

        if not is_dependency_installed(self.tool_name):
            raise ValueError(f"{self.tool_name} is either invalid or not installed.")

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.tool_name!r})"


class Options:

    # global variable
    user_options = {}

    def __init__(self):
        self.selected_options = {}


# pylint: disable= consider-using-dict-items, redefined-builtin
class Iperf3(Options):
    """
    Validate whether Selected options and there value are correct

    Returns:
        user_selected_options: dict
            A dictionary with correct options
    """

    # pylint: disable= too-many-arguments, unused-argument
    @staticmethod
    @input_validator
    def server_option(
        s_verbose: bool = False,
        s_interval: float = 0.2,
        s_format: str = None,
        s_logfile: str = None,
        s_forceflush: bool = False,
        s_timestamps: str = None,
        port_no: int = None,
        one_off: bool = True,
        bitrate: str = None,
        daemon: bool = False,
    ):
        """
        select options to configure iperf3 server

        Returns:
            selected_option: dict
                valid selected options for iperf3  server configuration
        """
        Iperf3.user_options = {}
        for option, val in locals().items():
            if val:
                Iperf3.user_options.update({option: val})
        return Iperf3.user_options

    @staticmethod
    @input_validator
    def client_option(
        verbose: bool = False,
        interval: float = 0.2,
        format: str = None,
        logfile: str = None,
        forceflush: bool = False,
        timestamps: str = False,
        cport: int = None,
        target_bw: str = None,
    ):
        """
        select options to configure iperf3 client

        Returns:
            selected_option: dict
                valid selected options for iperf3 client configuration
        """
        Iperf3.user_options = {}
        for option, val in locals().items():
            if val:
                Iperf3.user_options.update({option: val})
        return Iperf3.user_options

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.user_options!r})"


@input_validator
class Iperf3Options(Options):
    """
    Validate whether Selected options and there value are correct

    Returns:
        user_selected_options: dict
            A dictionary with correct options
    """

    # server options
    s_verbose: bool
    s_interval: float
    s_format: str
    s_logfile: str
    s_forceflush: bool
    s_timestamps: str
    port_no: int
    one_off: bool
    bitrate: str
    daemon: bool

    # client options
    verbose: bool
    interval: float
    format: str
    logfile: str
    forceflush: bool
    forceflush: bool
    timestamps: str
    cport: int
    protocol: str
    target_bw: str
    cong_algo: str
    kwargs: dict

    # pylint: disable= consider-using-dict-items
    def __init__(self, kwargs: dict = None):

        super().__init__()

        default_Options = {
            "default_server_options": {
                "s_verbose": False,  # more detailed output as a log file
                "s_interval": 0.2,  # Generate interim results every INTERVAL seconds
                "s_format": None,  # format to report: Kbits, Mbits, Gbits, Tbits
                "s_logfile": None,  # send output to a log file
                "s_forceflush": False,  # force flushing output at every interval
                "s_timestamps": None,  # generate timestamp at the start of each output line
                "port_no": None,  # server port to listen on(#generated randomely)
                "one_off": True,  # handle one client connection then exit
                "bitrate": None,  # server's total bit rate limit
                "daemon": False,  # run server as daemon
            },
            "default_client_options": {
                "verbose": False,  # more detailed output as a log file
                "interval": 0.2,  # Generate interim results every INTERVAL seconds
                "format": None,  # format to report: Kbits, Mbits, Gbits, Tbits
                "logfile": None,  # send output to a log file
                "forceflush": False,  # force flushing output at every interval
                "timestamps": None,  # generate timestamp at the start of each output line
                "cport": None,  # bind to a specific client port
                "protocol": None,  # protocol name which is going to be used
                "target_bw": "1mbit",  # target bitrate in bits/sec at client side
                "cong_algo": "cubic",  # set TCP congestion control algorithm
            },
        }

        # Validate the dictionary passed and set the internal data members
        for _, Option in default_Options.items():
            for Option_key in Option:
                if Option_key in kwargs:
                    if kwargs[Option_key]:
                        self.selected_options.update({Option_key: kwargs[Option_key]})
                    continue
                if Option[Option_key]:
                    self.selected_options.update({Option_key: Option[Option_key]})

    def getter(self, protocol="tcp"):
        """
        Get Iperf3 command line options based on user selected options
        """

        if protocol == "tcp":
            return self.selected_options
        if protocol == "udp":
            # TODO: Handling udp protocol a bit hackily here.
            # Manually removing the "cong_algo" parameter
            # for UDP flows since it's not related to UDP
            selected_options = self.selected_options
            if "cong_algo" in selected_options:
                del selected_options["cong_algo"]
            return selected_options

        return None

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.selected_options!r})"
