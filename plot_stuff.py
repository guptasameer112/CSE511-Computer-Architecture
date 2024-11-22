from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
from typing import List

def plot_stuff(dirs: List[str], req_data: str, plot_name: str, plot_heading: str):
    expoff_x, expoff_y = get_data(dirs[0], req_data)
    tp_x, tp_y = get_data(dirs[1], req_data)
    
    plt.plot(expoff_x, expoff_y, marker='v', linestyle='-', label="expoff", color="#6da8ca")
    plt.plot(tp_x, tp_y, marker="s", linestyle="-", label="token_passing", color="#82c98b")
    plt.title(plot_heading)
    plt.xlabel('Wireless Channel Bandwidth (GB/s)')
    plt.ylabel('Execution time on host (sec)')
    
    plt.legend()
    plt.savefig("plots/" + plot_name, dpi=300)

def plot_packets(dirs: List[str], req_data: str, plot_name: str, plot_heading: str):
    expoff_x, expoff_y = get_data(dirs[0], req_data)
    tp_x, tp_y = get_data(dirs[1], req_data)
    
    expoff_y = np.divide(expoff_y, 10**6)
    tp_y = np.divide(tp_y, 10**6)
    
    # print(expoff_y, tp_y)
    
    plt.plot(expoff_x, expoff_y, marker='v', linestyle='-', label="expoff", color="#6da8ca")
    plt.plot(tp_x, tp_y, marker="s", linestyle="-", label="token_passing", color="#82c98b")
    plt.title(plot_heading)
    plt.xlabel('Wireless Channel Bandwidth (GB/s)')
    plt.ylabel('Number of transmissions (million)')
    
    plt.legend()
    # plt.show()
    plt.savefig("plots/" + plot_name, dpi=300)
    
def get_data(dirname: str, req_data: str):
    # get them files
    folder = Path('output/' + dirname)
    files = list(folder.iterdir())

    data = []
    x_axis = []
    
    # get info from every file
    for file in files:
        # open that thang
        with file.open() as f:
            for line in f:
                if req_data in line:
                    bandwidth = str(file).split("GHZ")[1].split(".txt")[0]
                    
                    # correction for 12.5 GB/s case
                    if bandwidth == "12_5":
                        bandwidth = 12.5
                    x_axis.append(float(bandwidth))
                    
                    # print(bandwidth)
                    # print(line)
                    tokens = line.split()
                    data.append(float(tokens[1]))
                    break
    
    # correcting data order to ensure 1 to 1 correspondence
    x = np.array(x_axis)
    y = np.array(data)
    sort_idx = np.argsort(x)
    x_sorted = x[sort_idx]
    y_sorted = y[sort_idx]
    
    return x_sorted, y_sorted
                
plot_stuff(["per_core/expoff", "per_core/token_pass"], "host_seconds", "exec_time_per_core.png", "Execution Times for Wireless Interconnects in per-core Config")
plt.close("all")
plt.rcdefaults()
plot_packets(["per_core/expoff", "per_core/token_pass"], "system.membus.pkt_count::total" , "transmissions_per_core.png", "Packets Exchanged Across Wireless Interconnect in per-core Config")
plt.close("all")
plt.rcdefaults()
plot_stuff(["per_cluster/expoff", "per_cluster/token_pass"], "host_seconds", "exec_time_per_cluster.png", "Execution Times for Wireless Interconnects in per-cluster Config")
plt.close("all")
plt.rcdefaults()
plot_packets(["per_cluster/expoff", "per_cluster/token_pass"], "system.membus.pkt_count::total", "transmissions_per_cluster.png", "Packets Exchanged Across Wireless Interconnect in per-cluster Config")
