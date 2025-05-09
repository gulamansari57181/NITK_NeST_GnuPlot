# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Plot ping results"""

import logging
import matplotlib.pyplot as plt
import pandas as pd
from nest import config
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import simple_plot, simple_gnu_plot

logger = logging.getLogger(__name__)


def _plot_ping_flow(flow, node, dest):
    """
    Plot ping stats of the flow

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    flow : List
        List with timestamps and stats
    node : str
        Node from which ping results were obtained from
    dest :
        Destination ip:port address of the flow

    Returns
    -------
    tuple/None
        Timestamped rtt values
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        logger.warning(
            "Flow from %s to destination %s " "doesn't have any parsed ping result.",
            node,
            dest,
        )
        return None

    # First item is the "meta" item with user given information
    destination_node = flow[0]["destination_node"]

    # "Bias" actual start_time in experiment with user given start time
    start_time = float(flow[1]["timestamp"]) - float(flow[0]["start_time"])

    timestamp = []
    rtt = []

    for data in flow[1:]:
        rtt.append(float(data["rtt"]))
        # add relative time in timestamp
        timestamp.append(float(data["timestamp"]) - start_time)

    fig = simple_plot(
        "",
        timestamp,
        rtt,
        ["Time (Seconds)", "Ping Latency (ms)"],
        legend_string=f"{node} to {destination_node} ({dest})",
    )
    base_filename = f"ping_{node}_to_{destination_node}({dest})"
    Pack.dump_plot("ping", f"{base_filename}.png", fig)
    plt.close(fig)
    if config.get_value("enable_gnuplot"):
        data_frame = pd.DataFrame(list(zip(timestamp, rtt)))
        Pack.dump_datfile("ping", base_filename + ".dat", data_frame)

        # Store paths in a dict for .dat, .eps and .plt
        paths = {
            "dat": Pack.get_path("ping", f"{base_filename}.dat"),
            "eps": Pack.get_path("ping", f"{base_filename}.eps"),
            "plt": Pack.get_path("ping", f"{base_filename}.plt"),
        }

        legend_string = f"{node} to {destination_node} ({dest})"
        simple_gnu_plot(
            paths,
            ["Time (Seconds)", "Ping Latency (ms)"],
            legend_string,
        )

    return (timestamp, rtt)


@handle_keyboard_interrupt
def plot_ping(parsed_data):
    """
    Plot statistics obtained from ping

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from ss
    """
    for node in parsed_data:
        node_data = parsed_data[node]

        for connection in node_data:
            for dest in connection:
                flow = connection[dest]
                _plot_ping_flow(flow, node, dest)
