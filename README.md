DKit for Sublime Text
---------------------

DKit is a package to aid developing D programs using Sublime Text 3.

Features
--------

- Autocompletion using [DCD](https://github.com/Hackerpilot/DCD) (D Completion Daemon).
- Integration with [DUB](http://code.dlang.org/) build system.
- Simple build systems using `rdmd` and `dub`.

TODO
----

- Find a better way to show call tips (there are some sublime text limitations).
- Better DUB integration

Installation
------------

Currently I would like to postpone supporting Sublime Package Control installation until things stabilize with the plugin and proper testing is done on all platforms.
Only Linux has been tested so far. Although it should work properly on other operating systems. (I welcome any feedback)

To install the plugin:

1. Clone this repository into your Sublime Text packages folder. You can find where your folder is located by clicking on 'Preferences -> Browse Packages'. Alternatively, on Linux, look in your ~/.config/sublime-text-3/Packages/, or in sublime-text-3\Data\Packages on Windows.

2. You'll need to install [DCD](https://github.com/Hackerpilot/DCD) first. Follow the steps in DCD's [readme](https://github.com/Hackerpilot/DCD/blob/master/README.md#setup).
  1. Do not run the server. DKit will automatically run the server when needed.
  2. Go to 'Preferences -> Package Settings -> DKit -> Settings - User', and set it up like 'Settings - Default' to match your system. Notably you need to set dcd_path to your DCD's installation path.
  3. Setup include_paths to your DMD installation.
    + On Linux, the default path to your includes are `/usr/include/dmd/phobos` and `/usr/include/dmd/druntime/import`
    + On Windows, you should have your includes point to `d\\src\\phobos` and `d\\src\\druntime\\import`
  4. You can also add include_paths per project.

3. To use DUB features, you'll need to have [DUB](https://github.com/rejectedsoftware/dub#installation) installed and in your PATH environment variable.

Available Commands
------------------

- DKit: Restart DCD Autocompletion Server
  - If you notice that the autocompletion stopped working, try running this command to resolve the issue.
- DKit: Update Import Paths
  - If you have just added a new file to your project or created a Sublime project from a DUB package, run this command to update the imports.
- DKit: List Installed DUB Packages
  - This command lists the DUB packages installed as reported by DUB.
- DKit: Create DUB Package File
  - This command creates a dub package template file.
- DKit: Create Project From DUB Package File
  - You can create a Sublime project from a DUB package file using this command. Open the DUB package file, then run this to create the project.


Troubleshooting
---------------

- If you find that your includes are not being suggested, try running `DKit: Update Import Paths` command in Sublime.
- If you notice that the autocompletion stopped working, try running `DKit: Restart DCD Autocompletion Server` command in Sublime.
- For other problems, please use the issue tracker.

Questions
---------

Please use GitHub's issue tracker for questions and problems.
