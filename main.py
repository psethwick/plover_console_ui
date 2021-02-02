# -*- coding: utf-8 -*-
# Copyright (c) 2013 Hesky Fisher
# See LICENSE.txt for details.

"Launch the plover application."


import argparse
import atexit
import os
import sys
import subprocess
import traceback

from plover.config import Config
from plover.oslayer import processlock
from plover.oslayer.config import CONFIG_DIR
from plover.registry import registry
from plover import log
from plover import __name__ as __software_name__
from plover import __version__

CONFIG_FILE = "C:\\Users\\riders\\AppData\\Local\\plover\\plover\\plover.cfg"

def init_config_dir():
    """Creates plover's config dir.

    This usually only does anything the first time plover is launched.
    """
    # Create the configuration directory if needed.
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    # Create a default configuration file if one doesn't already exist.
    if not os.path.exists(CONFIG_FILE):
        open(CONFIG_FILE, 'wb').close()


def main():
    """Launch plover."""
    description = "Run the plover stenotype engine. This is a graphical application."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--version', action='version', version='%s %s'
                        % (__software_name__.capitalize(), __version__))
    parser.add_argument('-s', '--script', default=None, nargs=argparse.REMAINDER,
                        help='use another plugin console script as main entrypoint, '
                        'passing in the rest of the command line arguments, '
                        'print list of available scripts when no argument is given')
    parser.add_argument('-l', '--log-level', choices=['debug', 'info', 'warning', 'error'],
                        default=None, help='set log level')
    parser.add_argument('-g', '--gui', default=None, help='set gui')
    args = parser.parse_args(args=sys.argv[1:])
    if args.log_level is not None:
        log.set_level(args.log_level.upper())
    log.setup_platform_handler()

    log.info('Plover %s', __version__)
    log.info('configuration directory: %s', CONFIG_DIR)

    registry.update()

    if args.gui is None:
        gui_priority = {
            'qt': 1,
            'none': -1,
        }
        gui_list = sorted(registry.list_plugins('gui'), reverse=True,
                          key=lambda gui: gui_priority.get(gui.name, 0))
        gui = gui_list[0].obj
    else:
        gui = registry.get_plugin('gui', args.gui).obj

    try:
        # Ensure only one instance of Plover is running at a time.
        with processlock.PloverLock():
            if sys.platform.startswith('darwin'):
                appnope.nope()
            init_config_dir()
            # This must be done after calling init_config_dir, so
            # Plover's configuration directory actually exists.
            log.setup_logfile()
            config = Config()
            config.target_file = CONFIG_FILE
            code = gui.main(config)
            with open(config.target_file, 'wb') as f:
                config.save(f)
    except processlock.LockNotAcquiredException:
        gui.show_error('Error', 'Another instance of Plover is already running.')
        code = 1
    except:
        gui.show_error('Unexpected error', traceback.format_exc())
        code = 2
    if code == -1:
        # Restart.
        args = sys.argv[:]
        if args[0].endswith('.py') or args[0].endswith('.pyc'):
            # We're running from source.
            assert args[0] == __file__
            args[0:1] = [sys.executable, '-m', __spec__.name]
        # Execute atexit handlers.
        atexit._run_exitfuncs()
        if sys.platform.startswith('win32'):
            # Workaround https://bugs.python.org/issue19066
            subprocess.Popen(args, cwd=os.getcwd())
            code = 0
        else:
            os.execv(args[0], args)
    os._exit(code)

if __name__ == '__main__':
    main()
