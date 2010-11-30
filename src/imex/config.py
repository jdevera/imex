import optparse
import os

class ConfigManager(object):
    """
    Provide access to program options and/or configuration files
    """

    def __init__(self):
        self._cmdparser = None
        self._opts = None
        self._args = None
        self._default_config_file = os.path.expanduser('~/.imex')

        self._init_cmd_line_parser()


    def parse_cmd_line(self):
        """
        Parse the command line and return the verified config values
        """
        self._opts, self._args = self._cmdparser.parse_args()
        self._validate_cmd_line()
        return self._opts, self._args


    def _init_cmd_line_parser(self):
        """
        Add all available command line options
        """
        cmdparser = optparse.OptionParser()
        cmdparser.add_option('-r', '--rules',
            help = 'Use FILE as fules file',
            dest = 'rules_file',
            metavar = 'RULES_FILE')
        cmdparser.add_option('-c', '--check-rules',
            help = 'Perform rule validation',
            dest = 'check_rules',
            action = 'store_true',
            default = False)
        cmdparser.add_option('-t', '--update-time',
            help = 'Update the file timestamp when writing',
            action = 'store_false',
            dest = 'keep_times',
            default = True)
        cmdparser.add_option('-n', '--dry-run',
            help = 'Do not modify any image files',
            action = 'store_true',
            dest = 'dry_run',
            default = False)
        cmdparser.add_option('-d', '--debug',
            help = 'Show extra output with execution reports',
            action = 'store_true',
            dest = 'debug',
            default = False)
        cmdparser.add_option('-q', '--quiet',
            help = 'Do not show progress reports (still shows errors)',
            action = 'store_true',
            dest = 'quiet',
            default = False)

        self._cmdparser = cmdparser


    def _validate_cmd_line(self):
        """
        Make sure we have the minimum needed command line options and that they are correct.
        """
        if len(self._args) < 1:
            self._cmdparser.error('Need image file')

        if not self._opts.rules_file:
            msg = 'No rules file specified in command line'
            self._cmdparser.error(msg)
        elif not os.path.isfile(self._opts.rules_file):
            msg = 'Invalid rules file {0}'
            self._cmdparser.error(msg.format(self._opts.rules_file))

        if self._opts.debug and self._opts.quiet:
            msg = "Options 'debug' and 'quiet' are mutually exclusive."
            self._cmdparser.error(msg)


