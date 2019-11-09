from __future__ import print_function
import sys
import flow_layout
import os

from Qt import QtWidgets, QtGui, QtCore
from klauncher import solver
from klauncher import res


class LauncherDialog(QtWidgets.QMainWindow):
    def __init__(self):
        super(LauncherDialog, self).__init__()

        self.setWindowTitle('kLauncher')
        style_folder = os.environ.get("STYLE_KLAUNCHER")
        self.setWindowIcon(QtGui.QIcon(os.path.join(style_folder, "images/klauncher_logo/app_logo.png")))
        self.resize(455, 400)

        # Central layout
        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.project_combo = QtWidgets.QComboBox()
        self.sequence_combo = QtWidgets.QComboBox()
        self.shot_combo = QtWidgets.QComboBox()

        self.project_layout = QtWidgets.QHBoxLayout()
        self.project_layout.addWidget(self.project_combo)
        self.project_layout.addWidget(self.sequence_combo)
        self.project_layout.addWidget(self.shot_combo)

        self.project_layout.setSpacing(6)
        self.central_layout.addLayout(self.project_layout)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Flow layout
        self.flow_widget = QtWidgets.QWidget()
        self.flow_layout = flow_layout.FlowLayout()
        # self.flow_layout.setSpacing(10)
        self.flow_widget.setLayout(self.flow_layout)
        self.scroll_area.setWidget(self.flow_widget)
        self.central_layout.addWidget(self.scroll_area)

        self.central_layout.setContentsMargins(10, 20, 10, 10)
        self.central_layout.setSpacing(30)

        self.launcher_index = solver.launcherIndex()

        for i in sorted(self.launcher_index.projects()):
            self.project_combo.addItem(i, i)

        self.project_data = self.launcher_index.openCurrentProjectData(
            project=self.project_combo.itemText(0))

        self.onProjectComboChanged(0)
        self.onSequenceComboChanged(0)
        self.onShotComboChanged(0)

        self.project_combo.currentIndexChanged.connect(
            self.onProjectComboChanged)
        self.sequence_combo.currentIndexChanged.connect(
            self.onSequenceComboChanged)
        self.shot_combo.currentIndexChanged.connect(
            self.onShotComboChanged)

        with open(os.path.join(style_folder, "style.css"), 'r') as f:
            style = f.read()
        self.setStyleSheet(style)

    def onProjectComboChanged(self, index):
        self.current_project = self.project_combo.itemData(index)

        self.project_data = self.launcher_index.openCurrentProjectData(
            project=self.current_project)

        self.sequence_combo.blockSignals(True)
        self.sequence_combo.clear()

        seq = self.launcher_index.index[self.current_project]["sequences"]
        for i in sorted(seq):
            self.sequence_combo.addItem(i, i)

        self.sequence_combo.blockSignals(False)

        self.onSequenceComboChanged(self.sequence_combo.currentIndex())

    def onSequenceComboChanged(self, index):

        self.current_sequence = self.sequence_combo.itemData(index)

        self.shot_combo.clear()

        project = self.launcher_index.index[self.current_project]
        sequence = project["sequences"][self.current_sequence]

        for i in sorted(sequence["shots"]):
            self.shot_combo.addItem(i, i)

        self.onShotComboChanged(self.shot_combo.currentIndex())

    def onShotComboChanged(self, index):
        self.current_shot = self.shot_combo.itemData(index)

        self.populateTools(project=self.current_project)

    def populateTools(self, project):
        while self.flow_layout.count() > 0:
            item = self.flow_layout.takeAt(0)
            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()
        project_applications = self.launcher_index.getProjectApplications(
            project)

        for i in project_applications:
            applications = self.launcher_index.getApplications(i)

            tools = self.launcher_index.getProjectTools(
                self.project_data, i.name)

            for app in applications.keys():
                app_data = self.launcher_index.getApplicationData(i, app)
                widget = Application(name=app_data["label"],
                                     index=self.launcher_index,
                                     tools=tools,
                                     executable=app_data["executable"],
                                     project=project,
                                     sequence=self.current_sequence,
                                     shot=self.current_shot,
                                     logo=os.path.expandvars(app_data["image"]),
                                     hover=os.path.expandvars(app_data["hover"]))
                self.flow_layout.addWidget(widget)


class HoverFilter(QtCore.QObject):
    def eventFilter(self, widget, event):
        # effect = widget.graphicsEffect()
        if event.type() == QtCore.QEvent.Enter:

            widget.app_button.setIcon(QtGui.QIcon(widget.hover))

        if event.type() == QtCore.QEvent.Leave:
            widget.app_button.setIcon(QtGui.QIcon(widget.logo))

        return super(HoverFilter, self).eventFilter(widget, event)


class Application(QtWidgets.QFrame):

    def __init__(self, name, index, tools, executable, project, sequence, shot,
                 logo, hover, parent=None):
        super(Application, self).__init__(parent)
        self.name = name
        self.launcher_index = index
        self.tools = tools
        self.executable = executable
        self.project = project
        self.sequence = sequence
        self.shot = shot
        self.logo = logo
        self.hover = hover

        self.central_layout = QtWidgets.QVBoxLayout()

        self.setLayout(self.central_layout)
        self.event_filter = HoverFilter(self)

        self.app_button = QtWidgets.QToolButton()
        pixmap = QtGui.QPixmap(self.logo)
        size = QtCore.QSize(85, 85)
        pixmap = pixmap.scaled(size,
                               QtCore.Qt.KeepAspectRatioByExpanding,
                               QtCore.Qt.SmoothTransformation)

        self.app_button.setIcon(QtGui.QIcon(pixmap))
        self.app_button.setIconSize(size)
        self.app_button.setFixedSize(size)

        self.installEventFilter(self.event_filter)

        self.label = QtWidgets.QLabel(self.name)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.central_layout.addWidget(self.app_button)
        self.central_layout.addWidget(self.label)
        self.app_button.clicked.connect(self.onLoad)


    def onLoad(self):
        assets = os.environ.get("ASSETS")
        department = os.environ.get("DEPARTMENT")
        extra = {
            'PROJECT': self.project,
            'SEQUENCE': self.sequence,
            'SHOT': self.shot,
            'ASSETS': assets,
            'DEPARTMENT': department
        }
        self.launcher_index.launchApplication(tools=self.tools,
                                              executable=self.executable,
                                              extra_envs=extra)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = LauncherDialog()
    w.show()
    sys.exit(app.exec_())
