from __future__ import print_function
import sys
import os
import flow_layout
from Qt import QtWidgets
from launcher import solver



class LauncherDialog(QtWidgets.QDialog):
    def __init__(self):
        super(LauncherDialog, self).__init__()

        # Central layout
        self.central_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.central_layout)

        self.project_combo = QtWidgets.QComboBox()
        self.sequence_combo = QtWidgets.QComboBox()
        self.shot_combo = QtWidgets.QComboBox()

        self.project_layout = QtWidgets.QHBoxLayout()
        self.project_layout.addWidget(self.project_combo)
        self.project_layout.addWidget(self.sequence_combo)
        self.project_layout.addWidget(self.shot_combo)

        self.central_layout.addLayout(self.project_layout)

        # Flow layout
        self.flow_widget = QtWidgets.QWidget()
        self.flow_layout = flow_layout.FlowLayout()
        self.flow_layout.setSpacing(10)
        self.flow_widget.setLayout(self.flow_layout)

        self.launcher_index = solver.launcherIndex()

        for i in self.launcher_index.projects():
            self.project_combo.addItem(i, i)

        self.project_combo.currentIndexChanged.connect(self.onComboChanged)

        self.central_layout.addWidget(self.flow_widget)

    def onComboChanged(self, index):
        sel = self.project_combo.itemData(index)
        self.project_data = self.launcher_index.openCurrentProjectData(project=sel)
        self.populateTools(project=sel)

    def populateTools(self, project):
        while self.flow_layout.count() > 0:
            item = self.flow_layout.takeAt(0)
            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()
        applications = self.launcher_index.projectApplications(project)


        for i in applications:
            executables = self.launcher_index.applicationExecutables(i)
            tools = self.launcher_index.getToolsList(self.project_data, i.name)
            for executable in executables.keys():
                widget = Application(name= executable,
                                    index=self.launcher_index,
                                    tools=tools,
                                    executable=executable)
                self.flow_layout.addWidget(widget)


class Application(QtWidgets.QFrame):

    def __init__(self, name, index, tools, executable, parent=None):
        super(Application, self).__init__(parent)

        self.launcher_index = index
        self.tools = tools
        self.executable = executable

        self.central_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.central_layout)

        self.app_button = QtWidgets.QPushButton(name)
        self.central_layout.addWidget(self.app_button)
        self.app_button.clicked.connect(self.onLoad)

    def onLoad(self):
        self.launcher_index.launchApplication(self.tools, self.executable)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = LauncherDialog()
    w.show()
    sys.exit(app.exec_())
