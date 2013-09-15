DKit for Sublime Text
---------------------

DKit is a package to aid developing D programs using Sublime Text 3. It is still a work in progress.

Features
--------

- Autocompletion using [DCD](https://github.com/Hackerpilot/DCD) (D Completion Daemon).
- Integration with [DUB](http://code.dlang.org/) build system.
- Simple build systems using `rdmd` and `dub`.

TODO
----

- Find a better way to show call tips (there are some sublime text limitations).
- Better DUB integration
- Integrate addr2line for better stack traces

Installation
------------

Currently I would like to postpone supporting Sublime Package Control installation until things stabilize with the plugin and proper testing is done on all platforms.
Only Linux has been tested so far.

To install the plugin:

1. Clone this repository into your Sublime Text configurations folder. On Linux, that would be in your ~/.config/sublime-text-3/Packages/.

2. You'll need to install [DCD](https://github.com/Hackerpilot/DCD) first. Follow the steps in DCD's [readme](https://github.com/Hackerpilot/DCD/blob/master/README.md#setup).
  1. Do not run the server. DKit will automatically run the server when needed.
  2. Go to 'Preferences -> Package Settings -> DKit -> Settings - User', and set it up like 'Settings - Default' to match your system. Notably you need to set dcd_path to your DCD's installation path.
  3. Setup include_paths to your DMD installation.
  4. You can also add include_paths per project.

3. To use DUB features, you'll need to have [DUB](https://github.com/rejectedsoftware/dub#installation) installed and in your PATH environment variable.

Questions
---------

Please use GitHub's issue tracker for questions and problems.