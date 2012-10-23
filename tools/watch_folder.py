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
import datetime
import shutil
import random

class Console():
    @staticmethod
    def is_coloring_supported():
        return os.system == 'darwin'

    @staticmethod
    def format_message(msg):
        return "[{0}] {1}".format(datetime.datetime.now(), msg)

    @staticmethod
    def blank_line():
        Console.info("")

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


def safe_mkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def getDepends(xml_file_path):
    depend_list = []

    directory = os.path.split(xml_file_path)[0]

    file = open(xml_file_path, 'r')
    data = file.read()
    file.close()

    dom = parseString(data)

    for entity in dom.getElementsByTagName('parameter'):
        if entity.getAttribute('name') == 'filename':

            file_name_attr = entity.getAttribute('value')

            if (sys.platform == 'win32') or (sys.platform == 'win64'):
                file_name_attr = file_name_attr.replace('/', '\\')
            else:
                file_name_attr = file_name_attr.replace('\\', '/')

            depend_list.append(os.path.join( directory,  file_name_attr))

    return depend_list


def listAppleseedFiles(directory_path):
    directory_entities =  os.listdir(directory_path)
    files = []
    appleseed_files = []

    for entity in directory_entities:
        file_path = os.path.join(directory_path, entity)
        if os.path.isfile(file_path):
            if os.path.splitext(file_path)[1] == '.appleseed':
                appleseed_files.append(file_path)

    return appleseed_files


def isRenderable(file):
    depend_name_text = 'dependencies for "{0}"'.format(os.path.split(file)[1])
    Console.info(depend_name_text)
    Console.info(len(depend_name_text) * '-')

    is_renderable = True

    for depend in getDepends(file):
        if not os.path.exists(os.path.join(depend)):
            Console.error("MISSING {0}".format(depend))
            is_renderable = False

    Console.blank_line()

    return is_renderable


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

    output_dir = '_output'
    completed_dir = '_completed'
    log_dir = '_log'

    appleseed_dir = None
    watch_dir = None
    short_name = None

    for arg in sys.argv:
        if arg == '-h' or arg == '--help':
            print_usage()
            return 0
        split_arg = arg.split('=')
        if split_arg[0] == 'ad':
            appleseed_dir = split_arg[1]
        elif split_arg[0] == 'wd':
            watch_dir = split_arg[1]
        elif split_arg[0] == 'sn':
            short_name = split_arg[1]

    log_file_name = short_name + '.log'
    log_file_path = os.path.join(watch_dir, log_dir, log_file_name)

    if appleseed_dir is None:
        print("no path to appleseed provided.\n")
        print_usage()
        return 1

    if watch_dir is None:
        watch_dir = os.getcwd()
        print("no watch directory provided, watching working directory ({0}).\n".format(watch_dir))

    cli_path = os.path.join(appleseed_dir, 'appleseed.cli')

    if not os.path.exists(os.path.join(watch_dir, log_dir)):
        os.makedirs(os.path.join(watch_dir, log_dir))

    open(log_file_path, 'w').write('# file name : start time : end time : error status\n')

    while True:
        try:
            # wait until appleseed files are found
            appleseed_files = listAppleseedFiles(watch_dir)
            if len(appleseed_files) == 0:
                Console.info("nothing to render.")
                time.sleep(1)
                continue

            # define random start point for list
            random_start_point = int(random.random() * (len(appleseed_files) - 1))

            renderable_files_found = False
            start_time = None
            end_time = None
            reneder_file_name = None
            error_status = None

            # iterate over reordered list of files
            for appleseed_file in (appleseed_files[random_start_point:] + appleseed_files[:random_start_point]):
                Console.blank_line()

                if isRenderable(appleseed_file):
                    reneder_file_name = appleseed_file
                    start_time = datetime.datetime.now()

                    renderable_files_found = True

                    Console.success(':::: RENDERING "{0}" ::::\n'.format(appleseed_file))

                    # rename the appleseed file so others don't try to render it
                    in_progress_appendage = '.inprogress' if short_name is None else '.' + short_name
                    os.rename(appleseed_file, appleseed_file + in_progress_appendage)
                    appleseed_file += in_progress_appendage

                    # create shell command
                    appleseed_file_name = os.path.split(appleseed_file)[1]
                    output_file_name = os.path.splitext(appleseed_file_name)[0] + '.png'
                    output_file_path = os.path.join(watch_dir, output_dir, output_file_name)
                    command = '{0} -o "{1}" "{2}"'.format(cli_path, output_file_path, appleseed_file)

                    # make sure the output directory exists
                    safe_mkdir(os.path.join(watch_dir, output_dir))

                    # execute command
                    return_value = os.system(command)
                    Console.blank_line()

                    # if the return value is not 0 then something may have gone wrong
                    if return_value != 0:
                        Console.warning('file may not have rendered correctly: "{0}".'.format(appleseed_file))

                    # move the file into _completed directory
                    safe_mkdir(os.path.join(watch_dir, completed_dir))
                    move_dest = os.path.join(watch_dir, completed_dir, os.path.split(appleseed_file)[1])
                    shutil.move(appleseed_file, move_dest)

                    end_time = datetime.datetime.now()
                    error_status = 'success'

                    break

            if not renderable_files_found:
                time.sleep(1)

        except KeyboardInterrupt, SystemExit:
            Console.info("CTRL-C detected, exiting...")
            error_status = 'user exeted'
            break
        # except:
        #     Console.error("unexpected error: {0}.".format(sys.exc_info()[0]))
        #     error_status = 'enexpected error'
        #     pass

        if reneder_file_name is not None:
            log_line = '{0} : {1} : {2} : {3}\n'.format(reneder_file_name, start_time, end_time, error_status)
            open(log_file_path, "a+b").write(log_line)


if __name__ == '__main__':
    main()
