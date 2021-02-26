****************************
Console UI Plugin for Plover
****************************

This is a plugin for the open source stenography program `Plover <https://www.openstenoproject.org/plover/>`_

Requires Plover version 4.0.0 or later

.. image:: https://img.shields.io/pypi/v/plover_console_ui.svg
    :target: https://pypi.org/project/plover-console-ui/
.. image:: https://img.shields.io/pypi/dm/plover_console_ui.svg
    :target: https://pypi.org/project/plover-console-ui/

Installing
##########

1. Open Plover
2. Navigate to the Plugin Manager tool
3. Select 'plover_console_ui' in the list
4. Click install

Running - Linux/Mac
#########

Start plover with the --gui option:
`plover --gui console`

Running - Windows
#######

Due to some funky funky Windows workaround code (in plover), this plugin does not work will on the packaged Windows build

Here's a launcher that works:
`python -m plover --gui console`
(yes, it requires essentially 'run from source')
(I'm sorry)

Contributing
############

Head to the `open source repository <https://github.com/psethwick/plover_console_ui>`_

Issues + PRs welcome!
