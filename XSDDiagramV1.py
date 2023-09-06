import networkx as nx
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QFileDialog, QVBoxLayout, QWidget, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
import pydot
import os
import graphviz
from collections import deque

class XSDVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('XSD Visualizer')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        self.import_tab = QWidget()
        self.export_tab = QWidget()


        self.tab_widget.addTab(self.import_tab, "Import")
        self.tab_widget.addTab(self.export_tab, "Export")

        
        self.import_layout = QVBoxLayout(self.import_tab)
        self.export_layout = QVBoxLayout(self.export_tab)


        self.import_view = QGraphicsView(self)
        self.import_layout.addWidget(self.import_view)

        self.export_view = QGraphicsView(self)
        self.export_layout.addWidget(self.export_view)
        
        self.view_map = {
            self.import_tab: self.import_view,
            self.export_tab: self.export_view,

        }

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        open_file_action = file_menu.addAction('Open XSD File')
        open_file_action.triggered.connect(self.openXSD)

        self.import_graph = nx.DiGraph()
        self.export_graph = nx.DiGraph()


    def openXSD(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open XSD File', '', 'XSD Files (*.xsd);;All Files (*)')
        if file_name:
            xsd_root = ET.parse(file_name).getroot()
            self.build_xsd_graph(xsd_root, self.import_graph, self.export_graph)
            self.visualize_xsd_graph(self.import_graph, self.import_view, 'import_xsd_graph')
            self.visualize_xsd_graph(self.export_graph, self.export_view, 'export_xsd_graph')

            
    def build_xsd_graph(self, xsd_root, import_graph, export_graph):
        stack = deque([(xsd_root, None)])

        while stack:
            elem, parent_name = stack.pop()
            node_name = elem.attrib.get('name')  # Получаем значение атрибута 'name' или None, если его нет
            if self.should_add_to_graph(elem, parent_name):
                if node_name:
                    if node_name.startswith('import'):
                        graph = import_graph
                    elif node_name.startswith('export'):
                        graph = export_graph
                    else:
                        graph = None

                    if graph is not None:
                        graph.add_node(node_name)
                        if parent_name:
                            graph.add_edge(parent_name, node_name)

            # Теперь добавляем дочерние элементы в стек, их имена можно использовать
            for child in elem:
                stack.append((child, node_name if node_name else parent_name))
    
    def should_add_to_graph(self, child, parent_name):
        # Здесь вы можете добавить ваше условие для определения,
        # должен ли данный дочерний элемент быть добавлен в граф
        return 'name' in child.attrib
    
    def visualize_xsd_graph(self, graph, view, img_path):
        dot = graphviz.Digraph(format='png', engine='dot')

        for node in graph.nodes():
            dot.node(node, shape='ellipse')

        for edge in graph.edges():
            dot.edge(edge[0], edge[1], arrowhead='vee')

        img_path = os.path.join(os.path.dirname(__file__), img_path)
        dot.render(img_path, format='png', cleanup=True)

        scene = QGraphicsScene()
        view.setScene(scene)

        graph_image = QPixmap(img_path)
        scene.addPixmap(graph_image)

def main():
    app = QApplication(sys.argv)
    window = XSDVisualizer()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
