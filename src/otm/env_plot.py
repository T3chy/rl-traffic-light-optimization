from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.colors as pltc
import numpy as np

class plotEnv:

    def __init__(self):
        pass

    def plot_queue(self, ylim, title, green_stages, queue_vec, queue_times, signal_vec = None, signal_times = None, ybars = None):
        fig, ax = plt.subplots()
        ax.plot(queue_times, queue_vec)
        ax.set_ylim(ylim)

        if signal_vec != None:
            stages = np.array(signal_vec)
            aux = np.array([stages[i] if (i == 0 or stages[i-1] != stages[i]) else -1 for i in range(len(stages))])
            stages = np.extract(aux >= 0, stages)
            stage_times = np.extract(aux >=0, signal_times)
            changing_stages = np.array([stages[i] if (i == 0 or stages[i] in green_stages or (stages[i-1] in green_stages and stages[i] not in green_stages)) else -1 for i in range(len(stages))])
            stages = np.extract(changing_stages >= 0, stages)
            stage_times = np.extract(changing_stages >=0, stage_times)
            colors = ["g" if stages[i] in green_stages else "r" for i in range(len(stages))]
            for i in range(len(colors)):
                x_text_space = (stage_times[-1] - stage_times[0])*0.005
                ax.axvline(x=stage_times[i], color = colors[i])
                y = (ax.get_ylim()[1] - ax.get_ylim()[0])*0.96 + ax.get_ylim()[0]
                ax.text(stage_times[i] + x_text_space, y, stages[i] if stages[i] in green_stages else "")

        if ybars != None:
            for ybar in ybars:
                ax.axhline(y=ybar, color = "black", linestyle = "--")

        plt.ylabel("Number of vehicles")
        plt.xlabel("Time (seconds)")
        plt.title(title)
        plt.show()

    # def get_signal_positions(self, lines, control, link_ids, road_connection_info, controllers, signals): # PUT IN OTM4RL
    #
    #     link_coords = dict(zip(link_ids, lines))
    #     signal_positions = dict()
    #     for c_id, stage in control.items():
    #         phase_ids = controllers[c_id]["stages"][stage]["phases"]
    #         for phase_id in phase_ids:
    #             road_connections = signals[c_id]["phases"][phase_id]["road_conns"]
    #             for road_connection in road_connections:
    #                 in_link_id = road_connection_info[road_connection]["in_link"]
    #                 out_link_id = road_connection_info[road_connection]["out_link"]
    #                 signal_positions[road_connection] = {"in_link": link_coords[in_link_id], "out_link": link_coords[out_link_id]}
    #     return signal_positions
    #
    # def network_gradient(self, queues, control):
    #     fig, ax = plt.subplots()
    #
    #     lines, minX, maxX, minY, maxY = self.build_network_lines(queues)
    #
    #     norms.append(queues[link_id]["waiting"]/self.max_queues[link_id]) # CHANGE
    #
    #     cmap = plt.get_cmap('Wistia')
    #     all_colors = [cmap(z) for z in norms]
    #     lc = LineCollection(lines, colors = all_colors)
    #     lc.set_linewidths(15)
    #     ax.add_collection(lc)
    #
    #     dY = maxY - minY
    #     dX = maxX - minX
    #
    #     if (dY > dX):
    #         ax.set_ylim((minY, maxY))
    #         c = (maxX + minX) / 2
    #         ax.set_xlim((c - dY / 2, c + dY / 2))
    #     else:
    #         ax.set_xlim((minX, maxX))
    #         c = (maxY + minY) / 2
    #         ax.set_ylim((c - dX / 2, c + dX / 2))
    #
    #     signal_positions = self.get_signal_positions(lines, control)
    #
    #     for rc in signal_positions.values():
    #         p0 = rc["in_link"][0]
    #         p1 = rc["in_link"][1]
    #         ax.annotate(s='', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='-'))
    #         p0 = rc["out_link"][0]
    #         p1 = rc["out_link"][1]
    #         ax.annotate(s='', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='->'))
    #
    #     plt.show()
        # plot traffic lights
        # show time
