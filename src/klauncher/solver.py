from __future__ import print_function
import os
import json
import ecosystem
import subprocess
import re


class launcherIndex(object):
    def __init__(self):

        self.project_def_path = os.environ.get("PROJECT_DEF_PATH")
        self.project_index_path = os.environ.get("PROJECTS_INDEX_PATH")

        with open(os.environ.get("PROJECTS_INDEX_PATH"), 'r') as file:
            self.index = json.load(file)

        with open(os.getenv('APP_CONFIG_PATH'), 'r') as file:
            self.application_config = json.load(file)

        self.common_def_path = os.path.join(self.project_def_path,
                                            'common.json')

        self.ecosystem = ecosystem.Ecosystem()

    def projects(self):
        return self.index.keys()

    def openCurrentProjectData(self, project):
        project_data_path = os.path.join(self.project_def_path,
                                         '{}.json'.format(project))

        if not os.path.isfile(project_data_path):
            project_data_path = self.common_def_path

        with open(project_data_path, "r") as file:
            project_data = json.load(file)

        return project_data

    def getProjectApplications(self, project):
        project_data = self.openCurrentProjectData(project)

        tools = []
        for app in project_data['applications']:
            tools.append(self.ecosystem.get_tool(app))
        return tools

    def getProjectTools(self, project_data, app):
        tools = []
        for regex, values in project_data['tools'].items():
            if re.match(regex, app):
                tools += values
        tools.append(app)
        return tools

    def getApplications(self, tool):
        return self.application_config[tool.tool]

    def getApplicationData(self, tool, executable):
        return self.application_config[tool.tool][executable]

    def launchApplication(self, tools, executable, extra_envs=None):

        env = self.ecosystem.get_environment(*tools)

        with env:
            env = dict(os.environ.copy())

            if extra_envs:
                env.update(extra_envs)
            if isinstance(executable, list) is True:
                _executable = []
                for i in executable:
                    expanded = os.path.expandvars(i)
                    _executable.append(expanded)
                executable = _executable

            else:
                executable = os.path.expandvars(executable)

            env = {str(x): str(y) for x, y in env.items()}
            subprocess.Popen(executable, env=env)
