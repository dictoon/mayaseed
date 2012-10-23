
#
# Copyright (c) 2012 Jonathan Topf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


from xml.dom.minidom import parseString
import os
import sys
import time
from datetime import datetime
import shutil
import random


def xstr(s):
    return "n/a" if s is None else str(s)


def safe_mkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


class Console:
    @staticmethod
    def is_coloring_supported():
        return os.system == 'darwin'

    @staticmethod
    def format_message(msg):
        return "[{0}] {1}".format(datetime.now(), msg)

    @staticmethod
    def info(msg):
        print("{0}".format(Console.format_message(msg)))

    @staticmethod
    def success(msg):
        s = Console.format_message(msg)
        if Console.is_coloring_supported():
            print("\033[92m{0}\033[0m".format(s))
        else:
            print("{0}".format(s))

    @staticmethod
    def warning(msg):
        s = Console.format_message(msg)
        if Console.is_coloring_supported():
            print("\033[93m{0}\033[0m".format(s))
        else:
            print("{0}".format(s))

    @staticmethod
    def error(msg):
        s = Console.format_message(msg)
        if Console.is_coloring_supported():
            print("\033[91m{0}\033[0m".format(s))
        else:
            print("{0}".format(s))


class Log:
    def __init__(self, path):
        self.path = path
        self.reset()
        self.emit("# beginning logging {0}".format(datetime.now()))

    def reset(self):
        self.project_file = None
        self.start_time = None
        self.end_time = None

    def begin_rendering(self, project_file):
        self.project_file = project_file
        self.start_time = datetime.now()

    def end_rendering(self):
        self.end_time = datetime.now()
        self.message("success")
        self.reset()

    def message(self, msg):
        self.emit("{0} : {1} : {2} : {3}".format(xstr(self.project_file), xstr(self.start_time), xstr(self.end_time), xstr(msg)))

    def emit(self, msg):
        with open(self.path, "a") as file:
            file.write(msg + "\n")


def get_project_files(directory):
    project_files = []

    for entity in os.listdir(directory):
        file_path = os.path.join(directory, entity)
        if os.path.isfile(file_path):
            if os.path.splitext(file_path)[1] == '.appleseed':
                project_files.append(file_path)

    return project_files


def get_missing_project_dependencies(project_file):
    missing_deps = []

    directory = os.path.split(project_file)[0]

    with open(project_file, 'r') as file:
        data = file.read()

    for entity in parseString(data).getElementsByTagName('parameter'):
        if entity.getAttribute('name') == 'filename':
            filename = entity.getAttribute('value')

            if sys.platform == 'win32':
                filename = filename.replace('/', '\\')
            else:
                filename = filename.replace('\\', '/')

            filepath = os.path.join(directory, filename)

            if not os.path.exists(filepath):
                missing_deps.append(filepath)

    return missing_deps


def is_project_renderable(project_file):
    missing_deps = get_missing_project_dependencies(project_file)

    if len(missing_deps) == 0:
        return True

    Console.error('MISSING DEPENDENCIES for "{0}":'.format(os.path.split(project_file)[1]))

    for dep in missing_deps:
        Console.error("  {0}".format(dep))

    return False


def render_project(args, project_file):
    Console.success('RENDERING "{0}"...'.format(project_file))

    # rename the project file so others don't try to render it
    in_progress_appendage = '.inprogress' if args['short_name'] is None else '.' + args['short_name']
    os.rename(project_file, project_file + in_progress_appendage)
    project_file += in_progress_appendage

    # create shell command
    project_filename = os.path.split(project_file)[1]
    output_filename = os.path.splitext(project_filename)[0] + '.png'
    output_filepath = os.path.join(args['watch_dir'], args['output_dir'], output_filename)
    command = '{0} -o "{1}" "{2}"'.format(args['cli_path'], output_filepath, project_file)

    # make sure the output directory exists
    safe_mkdir(os.path.join(args['watch_dir'], args['output_dir']))

    # execute command
    result = os.system(command)
    if result != 0:
        Console.warning('file may not have rendered correctly: "{0}".'.format(project_file))

    # move the file into _completed directory
    safe_mkdir(os.path.join(args['watch_dir'], args['completed_dir']))
    move_dest = os.path.join(args['watch_dir'], args['completed_dir'], os.path.split(project_file)[1])
    shutil.move(project_file, move_dest)


def print_usage():
    print("usage:")
    print("  -h, --help   print this help")
    print("  ad=...       set appleseed bin directory")
    print("  wd=...       set watch directory")
    print("  sn=...       set short name, used to identify the file being rendered")


def main():
    if len(sys.argv) == 0:
        print_usage()
        return 0

    args = dict()

    args['output_dir'] = "_output"
    args['completed_dir'] = "_completed"
    args['log_dir'] = "_logs"

    args['appleseed_dir'] = None
    args['watch_dir'] = None
    args['short_name'] = None

    for arg in sys.argv:
        if arg == '-h' or arg == '--help':
            print_usage()
            return 0

        split_arg = arg.split('=')

        if split_arg[0] == 'ad':
            args['appleseed_dir'] = split_arg[1]
        elif split_arg[0] == 'wd':
            args['watch_dir'] = split_arg[1]
        elif split_arg[0] == 'sn':
            args['short_name'] = split_arg[1]

    if args['appleseed_dir'] is None:
        print("no path to appleseed provided.")
        print_usage()
        return 1

    if args['watch_dir'] is None:
        args['watch_dir'] = os.getcwd()
        print("no watch directory provided, watching working directory ({0}).".format(args['watch_dir']))

    args['cli_path'] = os.path.join(args['appleseed_dir'], 'appleseed.cli')

    log_dir = os.path.join(args['watch_dir'], args['log_dir'])
    log_filename = args['short_name'] + ".log"

    safe_mkdir(log_dir)
    log = Log(os.path.join(log_dir, log_filename))

    while True:
        try:
            # look for project files in the watch directory
            project_files = get_project_files(args['watch_dir'])

            # go to sleep for a while if no project file is found
            if len(project_files) == 0:
                Console.info("nothing to render.")
                time.sleep(3)
                continue

            # define random start point for list
            random_start_point = int(random.random() * (len(project_files) - 1))

            # iterate over reordered list of project files
            found_project = False
            for project_file in project_files[random_start_point:] + project_files[:random_start_point]:
                if is_project_renderable(project_file):
                    log.begin_rendering(project_file)
                    render_project(args, project_file)
                    log.end_rendering()
                    found_project = True
                    break

            # immediately look for the next project after a project was rendered
            if found_project:
                continue

        except KeyboardInterrupt, SystemExit:
            msg = "ctrl-c detected, exiting..."
            Console.info(msg)
            log.message(msg)
            break

        except:
            msg = "unexpected error: {0}.".format(sys.exc_info()[0])
            Console.error(msg)
            log.message(msg)
            pass

        # go to sleep for a while before the next cycle
        time.sleep(3)

if __name__ == '__main__':
    main()
