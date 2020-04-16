# !usr/bin/env python
# -*- coding : utf-8 -*-


import subprocess
import os
import shutil


from distutils.file_util import copy_file
from distutils.dir_util import copy_tree

CWD = os.path.abspath(os.path.join('..', 'pydkpro'))

def postShellCommand(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE)
    out = process.communicate()
    return out[0]

def postShellCommandInDirectory(command, destination):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, cwd=destination)
    out = process.communicate()
    return out[0]


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def copyAllFilesButOneTo(file_to_cut, destination):
    # list all files in current pipeline directory
    dirs = filter(os.path.isdir, os.listdir(os.getcwd()))
    files = filter(os.path.isfile, os.listdir(os.getcwd()))

    for file in files:
        copy_file(file, destination)

    for dir in dirs:

        if dir == file_to_cut:
            copy_tree(dir, os.path.join(destination, dir))


def writeFileAfterLineIdentifier(filePath, content, identifier):
    # get all lines of current file
    all_lines_in_file = open(filePath).readlines()

    # open file with override right
    with open(filePath, 'w') as filetowrite:

        alreadyWrittenCode = False
        # write every line from old document to the new document
        for line in all_lines_in_file:

            # check if writing the dependencies block startet
            # and check if not closing dependecies tag
            if identifier in line and not alreadyWrittenCode:

                # write dependencies line with line seperator
                filetowrite.write(line + "\n")

                for new_line in content:
                    filetowrite.write(new_line)

            else:
                filetowrite.write(line)

        filetowrite.close()





def addMavenDependencyToServer(path_to_pom, groupId, artifactId, version):
    # TODO Check for duplicates

    line_identifier = '@DKPRO component dependecies generation is starting this line'

    maven_dependency_to_add = [
        '\t\t<dependency>\n',
        '\t\t\t<groupId>' + groupId + '</groupId>\n',
        '\t\t\t<artifactId>' + artifactId + '</artifactId>\n',
        '\t\t\t<version>' + version + '</version>\n'
                                      '\t\t</dependency>\n'
    ]

    writeFileAfterLineIdentifier(path_to_pom, maven_dependency_to_add, line_identifier)

def findFilePath(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def generateImportStatement(path, java_import):

    # hard coded identifier into template
    identifier = '@DKPRO import code generation is starting this line'

    # the last thing todo: replace / with .
    path_to_import = 'import ' + java_import + ';\n'

    writeFileAfterLineIdentifier(path, path_to_import, identifier)


def generateAnalysisInit(path, java_import, parameters):
    identifier = '@DKPRO create pipeline components analysis, starting this line'


    classname = java_import.split('.')[-1]
    class_variable = classname.lower()

    if len(parameters.keys()) == 0:  # no parameters passed
        line1 = '\t\t' + 'AnalysisEngine ' + class_variable + ' = createEngine(' + classname + '.class);\n'
    else:
        #line1 = '\t\t' + 'AnalysisEngine ' + class_variable + ' = createEngine(' + classname + '.class);\n'
        line1 = '\t\t' + 'AnalysisEngine ' + class_variable + ' = createEngine(' + classname + '.class'
        for each_param in parameters.keys():
            line1 = line1 + ', "' + each_param + '",' + str(parameters[each_param])
        line1 = line1 + ');\n'

    java_code_to_add = [
        line1
    ]

    writeFileAfterLineIdentifier(path, java_code_to_add, identifier)


def generateAnalysisExec(path, java_import):
    classname = java_import.split('.')[-1]
    class_variable = classname.lower()
    identifier = '@DKPRO add pipeline components analysis, starting this line'
    line1 = '\t\t' + 'engines.add(' + class_variable + ');\n'


    java_code_to_add = [
        line1
    ]

    writeFileAfterLineIdentifier(path, java_code_to_add, identifier)


def generateJavaCode(path_to_dkpro_endpoint, groupId, artifactId, version, java_import, parameters):
    # file to rewrite
    pom_path = os.path.join(CWD, os.path.join('pipelines','pom.xml'))
    addMavenDependencyToServer(pom_path, groupId, artifactId, version)

    # the pipeline import and trigger has to be generated
    generateImportStatement(path_to_dkpro_endpoint, java_import)
    generateAnalysisInit(path_to_dkpro_endpoint, java_import, parameters)
    generateAnalysisExec(path_to_dkpro_endpoint, java_import)


def buildProject(path):
    commandBuilProject = ['mvn', 'clean', 'install', '-Dmaven.test.skip=true']
    postShellCommandInDirectory(commandBuilProject, path)


def setupFolders(boilerplate_path, pipeline_path):

    # path_destination = origin + '/' + deployment_folder_name
    postShellCommand(['mkdir', '-p',  pipeline_path])

    # copy current analysis files to deployment folder, without the deployment folder
    postShellCommand(['cp', '-r', os.path.join(boilerplate_path, '*'), pipeline_path])


def build_pipeline(required_pipeline):
    boilerplate_path = os.path.join(CWD, os.path.join( 'boilerplates', 'mypipeline'))
    pipeline_path = os.path.join(CWD, 'pipelines')
    if os.path.exists(pipeline_path):
        shutil.rmtree(pipeline_path)
    postShellCommand(['mkdir', '-p', pipeline_path])
    copytree(boilerplate_path, pipeline_path)
    path_to_dkpro_endpoint = os.path.join(CWD, os.path.join('pipelines', 'src', 'main', 'java', 'example',
                                                            'DKProPipeline.java'))
    for eachEntry in required_pipeline[::-1]:   # reversing the list
        class_name = eachEntry["class"]
        groupId = eachEntry["groupID"]
        artifactId = eachEntry["artifactId"]
        version = eachEntry["version"]
        java_import = eachEntry["java_import"]
        parameters = eachEntry["parameters"]
        generateJavaCode(path_to_dkpro_endpoint, groupId, artifactId, version, java_import, parameters)
    buildProject(pipeline_path)




