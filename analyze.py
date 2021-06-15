
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from enum import Enum
import numpy as np
from DIPPID import SensorUDP, SensorSerial, SensorWiimote
from DIPPID_pyqtnode import BufferNode, DIPPIDNode
import sys


class Axis(Enum):
    X = "X"
    Y = "Y"
    Z = "Z"
    NORMAL = "Normal"


class NormalVectorNode(Node):
    AXIS_1_IN = "axis1In"
    AXIS_2_IN = "axis2In"
    DATA_OUT = "dataOut"

    nodeName = "NormalVector"

    def __init__(self, name):
        terminals = {
            self.AXIS_1_IN: dict(io='in'),
            self.AXIS_2_IN: dict(io='in'),
            self.DATA_OUT: dict(io='out')
        }
        Node.__init__(self, name, terminals=terminals)

        self.normal_vector = ()

    def process(self, **kargs):
        """
        Processes the two inputs and returns the value
        accel_1 is negated because this seemed more intuitive on the device I tested with (Pixel 3)
        Without negating, the rotation would only be shown properly when pointing the charging port at the screen,
        instead of the usual "top" of the phone.
        """
        accel_1 = -kargs[self.AXIS_1_IN][0]  # negated because this seemed more logical on my device
        accel_2 = kargs[self.AXIS_2_IN][0]

        # didn't work with list of tuples, using np.array instead like in DIPPIDNode
        self.normal_vector = np.array([[0, 0], [accel_1, accel_2]])
        return {self.DATA_OUT: self.normal_vector}


fclib.registerNodeType(NormalVectorNode, [('Assignment 7',)])


class LogNode(Node):
    INPUT = "input"

    nodeName = "LogNode"

    def __init__(self, name):
        terminals = {
            self.INPUT: dict(io='in'),
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kargs):
        print(kargs[self.INPUT][0])


fclib.registerNodeType(LogNode, [('Assignment 7',)])


def create_plot_widget_x():
    pw_x = pg.PlotWidget()
    layout.addWidget(pw_x, 0, 1)
    pw_x.setYRange(-1, 1)
    pw_x.setTitle("X-Accelerometer")
    plot_widget_dict[Axis.X] = pw_x


def create_plot_widget_y():
    pw_y = pg.PlotWidget()
    layout.addWidget(pw_y, 0, 2)
    pw_y.setYRange(-1, 1)
    pw_y.setTitle("Y-Accelerometer")
    plot_widget_dict[Axis.Y] = pw_y


def create_plot_widget_z():
    pw_z = pg.PlotWidget()
    layout.addWidget(pw_z, 0, 3)
    pw_z.setYRange(-1, 1)
    pw_z.setTitle("Z-Accelerometer")
    plot_widget_dict[Axis.Z] = pw_z


def create_plot_widget_normal():
    pw_n = pg.PlotWidget()
    layout.addWidget(pw_n, 1, 2)
    pw_n.setYRange(-1, 1)
    pw_n.setXRange(-1, 1)
    pw_n.setTitle("Normal Vector")
    plot_widget_dict[Axis.NORMAL] = pw_n


def create_nodes():
    x_location = 250
    y_location = -100

    for key in plot_widget_dict:
        node = fc.createNode('PlotWidget', pos=(x_location, y_location))
        node.setPlot(plot_widget_dict[key])

        node_dict[key] = node
        y_location += 50


def connect_nodes():
    # DIPPID Nodes to Buffer Nodes
    fc.connectTerminals(dippid_node['accelX'], buffer_node_x['dataIn'])
    fc.connectTerminals(dippid_node['accelY'], buffer_node_y['dataIn'])
    fc.connectTerminals(dippid_node['accelZ'], buffer_node_z['dataIn'])

    # Buffer Nodes to PlotWidget Nodes
    fc.connectTerminals(buffer_node_x['dataOut'], node_dict[Axis.X]['In'])
    fc.connectTerminals(buffer_node_y['dataOut'], node_dict[Axis.Y]['In'])
    fc.connectTerminals(buffer_node_z['dataOut'], node_dict[Axis.Z]['In'])

    # Normal Vector Node - Rotation around Y axis
    fc.connectTerminals(dippid_node['accelX'], normal_vector_node[NormalVectorNode.AXIS_1_IN])
    fc.connectTerminals(dippid_node['accelZ'], normal_vector_node[NormalVectorNode.AXIS_2_IN])
    fc.connectTerminals(normal_vector_node[NormalVectorNode.DATA_OUT], node_dict[Axis.NORMAL]['In'])

    # Log Node
    fc.connectTerminals(dippid_node['accelX'], log_node[LogNode.INPUT])


def set_port_from_params():
    # if no parameter is passed, just use the default (5700)
    if len(sys.argv) == 1:
        return

    if len(sys.argv) > 2:
        print("Please pass only a port number as parameter")
        sys.exit(4)
    else:
        try:
            port = int(sys.argv[1])
            dippid_node.addr = port
            dippid_node.text.setText(sys.argv[1])
        except ValueError:
            print("Please pass a valid port number as parameter")
            sys.exit(4)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('DIPPIDNode demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={})
    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    plot_widget_dict = {}
    node_dict = {}

    create_plot_widget_x()
    create_plot_widget_y()
    create_plot_widget_z()
    create_plot_widget_normal()

    create_nodes()

    dippid_node = fc.createNode('DIPPID', pos=(0, -50))
    buffer_node_x = fc.createNode('Buffer', pos=(100, -100))
    buffer_node_y = fc.createNode('Buffer', pos=(100, -50))
    buffer_node_z = fc.createNode('Buffer', pos=(100, 0))
    normal_vector_node = fc.createNode(NormalVectorNode.nodeName, pos=(100, 50))
    log_node = fc.createNode(LogNode.nodeName, pos=(250, 100))

    set_port_from_params()

    connect_nodes()

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())
