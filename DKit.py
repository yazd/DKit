# -*- coding: utf-8 -*-

import sublime, sublime_plugin
from subprocess import Popen, PIPE, call
import os
import json
import sys
import time

plugin_settings = None
server_port = 9166
server_path = None
client_path = None

server_process = None

def get_shell_args(args):
    if sys.platform == 'win32':
        return args
    else:
        return ' '.join(args)

def read_settings(key, default):
    global plugin_settings
    if plugin_settings is None:
        plugin_settings = sublime.load_settings('DKit.sublime-settings')

    return sublime.active_window().active_view().settings().get(key, plugin_settings.get(key, default))

def read_all_settings(key):
    global plugin_settings
    if plugin_settings is None:
        plugin_settings = sublime.load_settings('DKit.sublime-settings')

    result = plugin_settings.get(key, [])
    result.extend(sublime.active_window().active_view().settings().get(key, []))
    return result

def open_file(filename):
    if sys.platform == 'win32':
        os.startfile(filename)
    else:
        opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        call([opener, filename])

def start_server():
    global server_process

    if not (server_process is None) and server_process.poll() is None:
        server_process.terminate()

    plugin_settings = sublime.load_settings('DKit.sublime-settings')

    global server_port
    server_port = read_settings('dcd_port', 9166)
    dcd_path = read_settings('dcd_path', '')

    global server_path
    global client_path
    server_path = os.path.join(dcd_path, 'dcd-server' + ('.exe' if sys.platform == 'win32' else ''))
    client_path = os.path.join(dcd_path, 'dcd-client' + ('.exe' if sys.platform == 'win32' else ''))

    if not os.path.exists(server_path):
        sublime.error_message('DCD server doesn\'t exist in the path specified:\n' + server_path + '\n\nSetup the path in DCD package settings and then restart sublime to get things working.')
        return False

    if not os.path.exists(client_path):
        sublime.error_message('DCD client doesn\'t exist in the path specified:\n' + client_path + '\n\nSetup the path in DCD package settings and then restart sublime to get things working.')
        return False

    include_paths = read_all_settings('include_paths')
    include_paths = ['-I' + p for p in include_paths]

    args = [server_path]
    args.extend(include_paths)
    args.extend(['-p' + str(server_port)])

    print('Restarting DCD server...')
    #print('Include paths: ')
    #print(include_paths)
    server_process = Popen(get_shell_args(args), shell=True)
    return True

class DCD(sublime_plugin.EventListener):
    def __exit__(self, type, value, traceback):
        global server_process
        if not (server_process is None) and server_process.poll() is None:
            server_process.terminate()

    def on_query_completions(self, view, prefix, locations):
        if view.scope_name(locations[0]).strip() != 'source.d':
            return

        global server_process
        if server_process is None:
            start_server()

        position = locations[0]
        position = position - len(prefix)
        if (view.substr(position) != '.'):
            position = locations[0]

        response = self.request_completions(view.substr(sublime.Region(0, view.size())), position)
        return (response, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def request_completions(self, file, position):
        args = [client_path, '-c' + str(position), '-p' + str(server_port)]
        client = Popen(get_shell_args(args), stdin=PIPE, stdout=PIPE, shell=True)

        output = client.communicate(file.encode())
        output = output[0].decode('utf-8').splitlines()
        if len(output) == 0:
            return []

        completions_type = output[0]
        del output[0]

        if (completions_type == 'identifiers'):
            output = [self.parse_identifiers(line) for line in output]
        elif (completions_type == 'calltips'):
            output = [self.parse_calltips(line) for line in output]
        else:
            output = []

        return output

    def parse_identifiers(self, line):
        parts = line.split('\t')

        if len(parts) == 2:
            cmap = {
                'c': 'class',
                'i': 'interface',
                's': 'struct',
                'u': 'union',
                'v': 'variable',
                'm': 'member variable',
                'k': 'keyword',
                'f': 'function',
                'g': 'enum',
                'e': 'enum member',
                'P': 'package',
                'M': 'module',
                'a': 'array',
                'A': 'associative array',
                'l': 'alias',
                't': 'template',
                'T': 'mixin template'}

            visible_name = parts[0] + '\t' + cmap.get(parts[1], ' ')
            if parts[1] == 'f':
                text = parts[0]
            else:
                text = parts[0]

            return visible_name, text

        else:
            return None

    def parse_calltips(self, line):
        index = line.find('(')
        if index >= 0:
            visible_name = line
            text = line[index + 1 : -1]
        else:
            visible_name = line
            text = line
        return visible_name, text

class DcdStartServerCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        start_server()

class DcdUpdateIncludePathsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global client_path
        Popen(get_shell_args([client_path, '--clearCache']), shell=True).wait()

        include_paths = set()
        for path in self.view.settings().get('include_paths', []):
            include_paths.add(path)

        if self.view.file_name():
            include_paths.add(os.path.dirname(self.view.file_name()))

        if len(include_paths) > 0:
            args = [client_path]
            args.extend(['-I' + p for p in include_paths])

            #print('Updating include paths:')
            #print(args)
            Popen(get_shell_args(args), shell=True).wait()

class DcdGotoDefinitionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global client_path
        if (len(self.view.sel()) != 1):
            sublime.error_message('Please set the cursor on the token to check.')
            return

        pos = self.view.sel()[0].a
        args = [client_path, '--symbolLocation', '-c ' + str(pos)]

        client = Popen(get_shell_args(args), stdin=PIPE, stdout=PIPE, shell=True)
        contents = self.view.substr(sublime.Region(0, self.view.size()))
        output = client.communicate(contents.encode())
        output = output[0].decode('utf-8').strip()
        if len(output) == 0 or output == 'Not found':
            sublime.error_message('No symbol definition found.')
            return

        output = output.split('\t', 1)
        path = output[0].strip()
        offset = int(output[1].strip())

        if path == 'stdin':
            new_view = self.view
        else:
            new_view = sublime.active_window().open_file(path)

        while not new_view.is_loading:
            time.sleep(0.005)

        view_region = sublime.Region(offset)
        new_view.sel().clear()
        new_view.sel().add(view_region)
        new_view.show_at_center(offset)

class DcdShowDocumentationCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global client_path
        if (len(self.view.sel()) != 1):
            sublime.error_message('Please set the cursor on the token to check.')
            return

        pos = self.view.sel()[0].a
        args = [client_path, '--doc', '-c ' + str(pos)]

        client = Popen(get_shell_args(args), stdin=PIPE, stdout=PIPE, shell=True)
        contents = self.view.substr(sublime.Region(0, self.view.size()))
        output = client.communicate(contents.encode())
        output = output[0].decode('utf-8').strip()
        if len(output) == 0 or output == 'Not found':
            sublime.error_message('No documentation found.')
            return
        
        docs = output.replace('\n', '\n\n')
        docs = docs.replace('\\n', '\n')

        panel = sublime.active_window().create_output_panel('ddoc')
        panel.insert(edit, 0, docs)
        sublime.active_window().run_command("show_panel", {"panel": "output.ddoc"})

class DubListInstalledCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            dub = Popen(get_shell_args(['dub', 'list']), stdin=PIPE, stdout=PIPE, shell=True)
            output = dub.communicate()
            output = output[0].splitlines()
            del output[0]
            output = [o.decode('utf-8').strip().partition(': ')[0] for o in output]
            output = [o for o in output if len(o) > 0]
            self.view.window().show_quick_panel(output, None)
        except OSError:
            sublime.error_message('Unable to run DUB. Make sure that it is installed correctly and on your PATH environment variable')

class DubCreatePackageCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.new_file()
        view.set_name('dub.json')
        view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
        view.run_command('dub_create_package_text')

class DubCreatePackageTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        package = """{
  "name": "project-name",
  "description": "An example project skeleton",
  "homepage": "http://example.org",
  "copyright": "Copyright (c) 2014, Your Name",
  "authors": [],
  "dependencies": {},
  "targetType": "executable"
}"""
        self.view.insert(edit, 0, package)

class DubCreateProjectFromPackageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        if view.file_name():
            package_folder = os.path.dirname(view.file_name())
            package_file = os.path.basename(view.file_name())

            if package_file != 'dub.json' and package_file != 'package.json':
                sublime.error_message('Please open the `dub.json` or `package.json` file and then run the command again.')
                return
        else:
            sublime.error_message('Please open the `dub.json` or `package.json` file and then run the command again.')
            return

        dub = Popen(get_shell_args(['dub', 'describe']), stdin=PIPE, stdout=PIPE, shell=True, cwd=package_folder)
        description = dub.communicate()
        description = description[0].decode('utf-8')

        if description.startswith('Checking dependencies'):
            end_of_line = description.find('\n')
            description = description[end_of_line:]

        try:
            description = json.loads(description)
        except ValueError:
            sublime.error_message('Please run DUB at least once to figure out dependencies before trying again. Aborting.') #TODO: change into something more user-friendly
            return

        include_paths = set()

        main_package = description['mainPackage']

        for package in description['packages']:
            base_path = package['path']
            for f in package['files']:
                folder = os.path.join(base_path, os.path.dirname(f['path']))
                include_paths.add(folder)

        folders = [{'path': folder} for folder in include_paths]
        settings = {'include_paths': [f for f in include_paths], 'package_file': view.file_name()}
        project_settings = {'folders': folders, 'settings': settings}

        project_file = os.path.join(package_folder, main_package + '.sublime-project')
        if os.path.exists(project_file):
            sublime.error_message('A Sublime Text project already exists in the folder. Aborting.') #TODO: change into something more user-friendly
            return

        f = open(project_file, "w")
        f.write(json.dumps(project_settings, indent=4))
        f.close()

        open_file(project_file)
