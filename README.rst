############################
Console UI Plugin for Plover
############################

This is a plugin for the open source stenography program `Plover <https://www.openstenoproject.org/plover/>`_

Requires Plover version 4.0.0 or later

.. image:: https://img.shields.io/pypi/v/plover_console_ui.svg
    :target: https://pypi.org/project/plover-console-ui/
.. image:: https://img.shields.io/pypi/dm/plover_console_ui.svg
    :target: https://pypi.org/project/plover-console-ui/


TODO gif goes here

##########
Installing
##########

1. Open Plover
2. Navigate to the Plugin Manager tool
3. Select ``plover_console_ui`` in the list
4. Click install

Or directly install ``plover_console_ui`` into plover's python environment

###############
Getting Started
###############

Linux/Mac
=========

Start plover with the --gui option:
``plover --gui console``

Running - Windows
=================

Due to some Windows workaround code (in plover), this plugin does not work well on the packaged Windows build

Here's a launcher that works:
``python -m plover --gui console``

Yes, it requires essentially 'run from source'... I'm sorry

#####
Usage
#####

This interface has a multi-level prompt and is fully keyboard driven

The ``help`` command is *always* available and will show all the currently
available commands

If a command has the description ``...`` there are further commands
contained inside

Commands can be partially entered (e.g. you can use ``m`` to use the ``machine``
command)

Case is ignored (e.g. ``configure`` is the same as ``CONFIGURE``).

To get back to the previous command level, press ``Enter`` on its own

If a command has ``<>`` in its description it takes one or more arguments. The type
of the argument is between the ``<>``

Commands
========

############
Contributing
############

Head to the `open source repository <https://github.com/psethwick/plover_console_ui>`_

Issues + PRs welcome!
