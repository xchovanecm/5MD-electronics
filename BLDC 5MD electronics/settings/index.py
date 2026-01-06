from PythonQt import *
import time
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import os
import shutil
from pathlib import Path


def test_executer(file, tests):
    for test in tests:
        status = eval(f"'{file}'{test}")
        if status:
            return False
    return True


class ProjectCreationHandler:
    def __init__(self, cw, application):
        self.cw = cw
        self.application = application

    def create_project(self, project_filename, project_name, project_description="Motor Control"):
        self.cw.newMCSProject(project_filename, project_name, project_description, "", "")
        print(f"Project '{project_name}' created")

    def add_instance(self, name, description, module, filename, domain, variants=""):
        self.cw.addInstance(name, description, module, filename, domain, variants)

    def _get_package_name(self):
        tree = ET.parse(f"{Path(self.cw.getLibDir()).parent}/package.xml")
        root = tree.getroot()
        for i in root.iter('library'):
            package = i.attrib['unique_id']

        return package

    def unzip_files_to_project(self, test_list):
        package = self._get_package_name()
        with ZipFile(f"{os.path.join(Path(self.cw.getLibDir()).parent,package)}.sdpack",'r') as zip:
            list_of_files = zip.namelist()
            destination_directory = Path(self.application.getScriptsDir()).parent
            for elem in list_of_files:
                if test_executer(elem, test_list):
                    self.cw.unZip(f"{os.path.join(Path(self.cw.getLibDir()).parent,package)}.sdpack", elem, destination_directory)

    def open_window(self, instance, domain):
        mdi_project_info = self.cw.searchInstance(instance, domain)

        if mdi_project_info:
            mdi_project_info.setFocus()
            mdi_project_info.showMaximized()
        else:
            print(f"Instance '{instance}' in domain '{domain}' does not exist")


if __name__.startswith('PythonQt'):
    # Create ProjectCreationHandler instance
    project_handler = ProjectCreationHandler(CW, application)

    # Unzip files from sdpack into project
    list_excluded_files = ["[file.rfind('/') +1 :].__eq__('index.py')", "[file.rfind('/') +1 :].__eq__('index.xml')",
                 "[file.rfind('/') +1 :].__eq__('package.xml')", "[file.rfind('/') +1 :].__eq__('installer.py')",
                 ".endswith('.sdpack')", ".endswith('.pxml')", ".endswith('.sdpack')", ".startswith('lib/')",
                 "[file.rfind('/') +1 :].__eq__('devicefunctions.xml')"]
    project_handler.unzip_files_to_project(list_excluded_files)
    print("copy folders completed!")

    # Create Project (mainly .cwproj file gets created)
    CW.showSplash("Create Project", "<font size=6>project creation in progress...</font>", 1)
    project_handler.create_project(CW.getProjectFilename(), CW.getProjectName())

    # Create Common instances 'main', 'dashboard', and 'mceos'
    project_handler.add_instance(name="main", description="Solution Designer",
                                 module="ProjectInfo", filename="Common_main.icwp",
                                 domain="Common")
    project_handler.add_instance(name="dashboard", description="Online dashboard",
                                 module="OperationView", filename="Common_dashboard.icwp",
                                 domain="Common")
    project_handler.add_instance(name="mceos", description="MCE global settings",
                                 module="MCEOS", filename="Common_mceos.icwp",
                                 domain="Common")

    CW.saveProject("")
    project_handler.open_window("main", "Common")
    CW.enableProjectTreeEdit(0)
    CW.hideSplash()

    print("Proj Name: " + CW.getProjectFilename())
    print("getScriptsDir: " + application.getScriptsDir())
    print("getWorkingDir: " + application.getWorkingDir())
    print("getXmlFilename: " + application.getXmlFilename())
    print("getXmlDir: " + application.getXmlDir())
    print("getLibDir: " + CW.getLibDir())
    print("getProjectFilename: " + CW.getProjectFilename())
    print("getProjectName: " + CW.getProjectName())
