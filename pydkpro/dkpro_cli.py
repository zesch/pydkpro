#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
# pylint: disable=no-value-for-parameter


import click      # package for easy cli generation
import subprocess # package to execute the shell,
import re
import os
import sys

from distutils.file_util import copy_file
from distutils.dir_util import copy_tree
from yaspin import yaspin
from yaspin.spinners import Spinners
import shutil

CWD = os.path.abspath(os.path.join('..', 'pydkpro'))
DKR = os.path.join('pipelines', 'deployment', 'target', 'docker')

def checkForFile(fileName):
    #return os.path.isfile('./' + fileName)
    return os.path.isfile(fileName)

def findFilePath(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def findDirPath(name, path):
    for root, dirs, files in os.walk(path):
        if name in dirs:
            return os.path.join(root, name)


def postShellCommand(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    out = process.communicate()
    return out[0]

def postShellCommandInDirectory(command, destination, origin):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, cwd=destination, shell=True)
    out = process.communicate()
    return out[0]


def removeSubstring(to_clean, substring):
    regExpression = '\\' + substring + '$'
    return re.sub(regExpression, '', to_clean)

def removeSubstrings(to_clean, substrings):
    _to_clean = ''
    for substring in substrings:
        _to_clean = removeSubstring(to_clean, substring)
    
    return _to_clean

def copyAllFilesButOneTo(file_to_cut, destination):

    # list all files in current pipeline directory
    dirs  = filter(os.path.isdir, os.listdir(os.getcwd()))
    files = filter(os.path.isfile, os.listdir(os.getcwd()))

    for file in files:
        copy_file(file, destination)

    for dir in dirs:
        
        if dir != file_to_cut:
            copy_tree(dir, os.path.join(destination, dir))


def writeFileAfterLineIdentifier(filePath, content, identifier):

    # get all lines of current file
    all_lines_in_file = open(filePath).readlines()

    # open file with override right 
    with open(filePath, 'w') as filetowrite:

        alreadyWrittenCode = False
        #write every line from old document to the new document
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

# for faster execution can be exchanged by commands like the following
# `echo -e 'setns x=http://maven.apache.org/POM/4.0.0\ncat /x:project/x:groupId/text()' | xmllint --shell pom.xml | grep -v /`
# i don't know how to execute them with subprocess

groupId_cmd = ['mvn', 'help:evaluate', '-Dexpression=project.groupId', '-q', '-DforceStdout']
artifactId_cmd = ['mvn', 'help:evaluate', '-Dexpression=project.artifactId', '-q', '-DforceStdout'] 
version_cmd = ['mvn', 'help:evaluate', '-Dexpression=project.version', '-q', '-DforceStdout'] 

# used global variables
# project file system path
origin = ''

#maven variables
groupId = ''
artifactId = ''
version = ''

# neccessary for code generation
className=''
methodName=''
imageName=''

# shows maven information in the terminal
def showMavenInformation():   
    click.secho('<groupId>' + str(groupId) + '<groupId>', fg='blue')
    click.secho('<artifactId>' + str(artifactId) + '<artifactId>', fg='blue')
    click.secho('<version>' + str(version) + '<version>', fg='blue')


    
def getPipelineMethodAndClassName():
    global className
    global methodName
    
    className = 'DKProPipeline'
    methodName = 'run'


    
def getPipelineMavenDependencyInformations():


    directory = os.path.join(CWD, 'pipelines')
    origin = 'PWD'
    global groupId
    global artifactId
    global version

    groupId    = postShellCommandInDirectory(groupId_cmd, directory, origin).decode('utf-8')
    artifactId = postShellCommandInDirectory(artifactId_cmd, directory, origin).decode('utf-8')
    version    = postShellCommandInDirectory(version_cmd,  directory, origin).decode('utf-8')

    # finalize
    #showMavenInformation()
    return True



def pullServerTemplateInFolder(folderName, origin):
    # server template, here is a good point to add multiple templates with a switch statement
    # the setup folder function could ask for a template specification in the shell

    deployment_path = os.path.join( 'pipelines', 'deployment')
    if os.path.exists(deployment_path):
        shutil.rmtree(deployment_path)
    postShellCommand(['mkdir', '-p', deployment_path])
    copytree(os.path.join(CWD, os.path.join('boilerplates', 'myapplication', 'dkpro-deploy-server-template')),
             os.path.join(CWD, os.path.join( 'pipelines','deployment')))


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        if not item == "deployment":
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

def setupFolders():
    # setup
    global origin
    deployment_folder_name = os.path.join(CWD, os.path.join( 'pipelines', 'deployment'))
    origin = postShellCommand(['pwd'])
    
    # path_destination = origin + '/' + deployment_folder_name 
    postShellCommand(['mkdir', '-p', deployment_folder_name] )

    # clone server git repository
    pullServerTemplateInFolder(deployment_folder_name, origin)

    # copy current analysis files to deployment folder, without the deployment folder
    analysis_folder_name = os.path.join(CWD, os.path.join('pipelines', 'deployment', 'pipeline'))
    postShellCommand(['mkdir', '-p', analysis_folder_name] )
    copytree(os.path.join(CWD, 'pipelines'), os.path.join(CWD, os.path.join('pipelines', 'deployment', 'pipeline')))
    postShellCommand(['mkdir', os.path.join(deployment_folder_name,'target' ,'docker')])

def addContainerName():
    print('in container name')
    path_to_pom = os.path.join('deployment', 'pom.xml')
    identifier = '@DKPRO CLI container name generation is starting this line'
    container_name= '<name>' + className + '</name>'

    writeFileAfterLineIdentifier(path_to_pom, container_name, identifier)     

def addMavenDependencyToServer():

    path_to_pom = os.path.join(CWD, os.path.join( 'pipelines', 'deployment', 'pom.xml'))
    line_identifier = '@DKPRO CLI import dependecies is starting this line'
    name_identifier = '@DKPRO CLI container name generation is starting this line'
    
    maven_dependency_to_add = [
        '\t\t<dependency>\n',
        '\t\t\t<groupId>' + str(groupId) + '</groupId>\n',
        '\t\t\t<artifactId>' + str(artifactId) + '</artifactId>\n',
        '\t\t\t<version>' + str(version) + '</version>\n'
        '\t\t</dependency>\n'
    ]

    container_name= '\t<name>' + str(className).lower() + '</name>'

    writeFileAfterLineIdentifier(path_to_pom, maven_dependency_to_add, line_identifier)
    writeFileAfterLineIdentifier(path_to_pom, container_name, name_identifier)



# Problem was to identify the import logic
def generateImportStatement(path):

    # hard coded identifier into template
    identifier = '@DKPRO CLI import code generation is starting this line'

    # create file name of class, maybe ask in cli if correct
    java_class_file_name = className + '.java'

    # to create a import statement we have to find the location of the class
    # in the project folder, this is the root from where we search the directory 
    # to locate the class file
    search_from = os.path.join(CWD, os.path.join( 'pipelines','src','main','java'))

    # executes the file search in the specified directory
    class_path = findFilePath(java_class_file_name, search_from)

    cleaned_path_java = class_path.replace('.java', '')
    cleaned_path = cleaned_path_java.replace(search_from, '')

    # the last thing todo: replace slash with .
    if sys.platform == 'win32':
        path_to_import = 'import ' + cleaned_path[1:].replace('\\', '.') + ';\n'
    else:
        path_to_import = 'import ' + cleaned_path[1:].replace('/', '.') + ';\n'

    writeFileAfterLineIdentifier(path, path_to_import, identifier)

def generateAnalysisInit(path):

    identifier = '@DKPRO CLI init static analysis, starting this line'

    line1 = '\t' + 'public static ' + className + ' analysis = new ' + className + '();\n'
    
    java_code_to_add = [
        line1
    ]

    writeFileAfterLineIdentifier(path, java_code_to_add, identifier)

def generateAnalysisExec(path):

    identifier = '@DKPRO CLI analysis code generation is starting this line'
    line1 = '\t\t\t' + 'JCas result = analysis.' + methodName + '(jsonString);\n'
    
    java_code_to_add = [
        line1
    ]

    writeFileAfterLineIdentifier(path, java_code_to_add, identifier)

def generateJavaCode():
    # file to rewrite
    path_to_dkpro_endpoint = os.path.join(CWD, os.path.join( 'pipelines', 'deployment', 'src', 'main', 'java', 'com',
                                                            'DKProEndpoint.java'))

    # the pipeline import and trigger has to be generated
    generateImportStatement(path_to_dkpro_endpoint)
    generateAnalysisInit(path_to_dkpro_endpoint)
    generateAnalysisExec(path_to_dkpro_endpoint)


def buildProject():
    path = os.path.join(CWD, os.path.join( 'pipelines', 'deployment'))
    commandBuilProject = ['mvn', 'clean', 'install', '-Dmaven.test.skip=true']
    postShellCommandInDirectory(commandBuilProject, path, origin)

def buildContainer():
    global imageName
    # this command compiles and builds the container image
    imageName = os.path.join('dkpro', className.lower())
    
    path = os.path.join(CWD, DKR)
    commandBuilding = ['docker', 'image','build', '-t', imageName, path]

    postShellCommand(commandBuilding) 

def pushContainertoRegistry():

    destination = os.path.join(CWD, os.path.join( 'pipelines', 'deployment'))

    # this command compiles and builds the container image
    command = ['mvn', 'clean', 'package', 'docker:build', '-DpushImageTag', '-DdockerImageTags=latest']
    postShellCommandInDirectory(command, destination, origin)

def runContainerLocally(background, port):

    destination = os.path.join(CWD,DKR)

    # get paths
    command_fg = ['docker', 'run', '-it', '--rm', '--name', 'dkpro_container',  '-p', port + ':8080', imageName]
    command_bg = ['docker', 'run', '-d', '--name', 'dkpro_container', '-p', port + ':8080', imageName]
    
    command = command_bg if background == True else command_fg
    postShellCommandInDirectory(command, destination, origin)

def moverDockerfilesAndRemoveDeployment():
    move = ['mv', os.path.join(CWD, DKR), 'docker']
    remove = ['rm' '-rf' ,os.path.join( 'pipelines','deployment')]
    postShellCommand(move)


def killAllRunningContainers():
    command = ['docker', 'rm', '--force', 'dkpro_container']
    postShellCommand(command)


def cliDefinition(port='3000', deploy='local', kill=False, background=True, only='', removeFolder=True, HTTPType='GET'):

    if isinstance(port, str) == False:
        port = port.toString()
    
    if kill == True: 
        killAllRunningContainers()
        return
    pomExists = checkForFile(os.path.join(CWD, os.path.join('pipelines', 'pom.xml')))

    if not pomExists:
        click.echo('No pom.xml found. Are you in the correct directory ?')
        return

    if only != 'deploy':
        got_information = getPipelineMavenDependencyInformations()


        getPipelineMethodAndClassName()

        click.secho('✓ Got all neccessary informations', fg='green')

        
        setupFolders()

        addMavenDependencyToServer()

        generateJavaCode()
        click.secho('✓ Server code generation', fg='green')

        with yaspin(text="Compiling Project", color="green") as sp:
            buildProject()

            sp.ok("✓")

    if deploy == 'local': 
        with yaspin( Spinners.pong ,text="Building container...", color="green") as sp:

            buildContainer()

            sp.ok("✓")

        if only != 'generate':
            with yaspin( Spinners.shark ,text="Container is running on port: " + port, color="blue") as sp:

                runContainerLocally(background, port)

    if deploy == 'registry':
        pushContainertoRegistry()
        click.secho('✓ Push container to registry', fg='green')



@click.command()
@click.option('--deploy', default='local', help='Can start local server or push container to registry, value = local || registry')
@click.option('--port', default='3000', help='You can specify the port when running locally, default port 3000')
@click.option('--kill', default=False, help='Kills all running containers, can be set to True, per default False')
@click.option('--background', default=True, help='When running the container locally you can deside if this programm should end by switching into the server logs, per default False')
@click.option('--only', default='', help='Can specify if the necessity exits to only run partially run the pipline, the pipeline can run with the values: deploy(if all necessary steps where either done manually or by the tool) and generate(only generates all necessary dependecies and code to run the server)')
@click.option('--remove', default=True, help='Specifies if the generated folder should be delted or be left in the directory')
@click.option('--type', default='GET', help='Specifies the HTTP method that should be called when executing the script. GET and POST is accepted, default value is GET)')
def main(port, deploy, kill, background, only, remove, type):
    
    try:
        cliDefinition(port='local', deploy='3000', kill=False, background=True, only='', remove=True, type='GET')

    except KeyboardInterrupt:
        click.secho('Exiting DKPro Deploy CLI', fg='red')
        sys.exit()
   
    
if __name__ == '__main__':
    main()
