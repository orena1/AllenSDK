# Copyright 2014-2015 Allen Institute for Brain Science
# Licensed under the Allen Institute Terms of Use (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.alleninstitute.org/Media/policies/terms_of_use_content.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from allen_wrench.config.app.pydev_connector import PydevConnector

try:
    from ConfigParser import ConfigParser # Python 2
except:
    from configparser import ConfigParser # Python 3

import argparse
import os
from pkg_resources import resource_filename

import logging
import logging.config as lc
import sys

class ApplicationConfig(object):
    ''' Convenience class that consolidates the handling of application configuration
        from environment variables, .conf files and the command line
        using Python standard libraries and formats.
    '''
    
    _log = logging.getLogger(__name__)
    _DEFAULT_LOG_CONFIG = resource_filename(__name__, 'logging.conf')
    lc.fileConfig(_DEFAULT_LOG_CONFIG)

    def __init__(self, 
                 defaults,
                 name="app",
                 halp="Run application.",
                 pydev=False,
                 default_log_config=None):
        self.application_name = name
        self.help = halp
        self.debug_enabled = False

        if default_log_config == None:
            default_log_config = ApplicationConfig._DEFAULT_LOG_CONFIG

        ApplicationConfig._log.info("default log config: %s" % (default_log_config))

        self.defaults = {
            'config_file_path': {
                'default': "%s.conf" % (self.application_name),
                'help': 'configuration file path'
            },
            'log_config_path': {
                'default': default_log_config,
                'help': 'logging configuration path'
            }
        }
        
        if pydev:
            self.debug_enabled = True
            self.defaults['debug'] = {
                'default': 'off',
                'help': 'pydev_remote or off (default)'
            }
 

        self.defaults.update(defaults)

        logging.info("defaults: %s" % (self.defaults))

        self.argparser = self.create_argparser()
                
        for key, value in self.defaults.items():
            setattr(self, key, value['default'])


    def load(self, command_line_args, disable_existing_loggers=True):
        ''' Load application configuration options, first from the environment,
            then from the configuration file, then from the command line.
            
            Each stage of loading can override the previous stage.
        '''
        # read and apply options from the environment
        self.apply_configuration_from_environment()
        
        # command line so we can find the config file.
        parsed_args = self.parse_command_line_args(command_line_args)

        try:
            # read and apply the configuration file options
            config_file_path = parsed_args.config_file_path
            if config_file_path:
                self.config_file_path = config_file_path
            self.apply_configuration_from_file(self.config_file_path)
            
            # apply the remaining command line options
            self.apply_configuration_from_command_line(parsed_args)
        except Exception as e:
            self.log.error("Could not load configuration file: %s\n%s" % 
                           (parsed_args.config_file_path,
                            e))

        if self.debug_enabled and self.debug.startswith('pydev'):
            PydevConnector.connect(self.debug)

        try:
            lc.fileConfig(self.log_config_path,
                          disable_existing_loggers=disable_existing_loggers)
        except:
            logging.error("Could not load log configuration file: %s" %
                         (parsed_args.log_config_path))


    def to_boolean(self, v):
        if str(v).lower() == 'true':
            return True
        
        return False  
   
   
    def create_argparser(self):
        parser = argparse.ArgumentParser(prog=self.application_name,
                                         description=self.help)
        # defaults are set at the first environment reading.  Command line args only override them when present

        for key, value in self.defaults.items():        
            if key == 'config_file_path':
                parser.add_argument("%s" % (key), default=None, help=value['help'])
            else:
                parser.add_argument("--%s" % (key), default=None, help=value['help'])
       
        return parser
    

    def parse_command_line_args(self, args):
        return self.argparser.parse_args(args)
    
    
    def apply_configuration_from_command_line(self, parsed_args):
        ''' Read application configuration variables from the command line.
            :param parsed_args: the arguments as parsed from the command line.
            :type parsed_args: dict
            
            Unassigned variables are left unchanged if previously assigned,
            set to their default values,
            or None if no default is specified at init time.
            Assigned variables will overwrite the previous value.
        
            see: https://docs.python.org/2/howto/argparse.html
        '''
        logging.info('command_line args: %s' % (parsed_args))
        
        for key in self.defaults:
            parsed_value = getattr(parsed_args, key)
            if parsed_value and getattr(self, key) is None:
                setattr(self, key, parsed_value)
    
    
    def apply_configuration_from_environment(self):
        ''' Read application configuration variables from the environment.
            The variable names are upper case and have a 
            prefix defined by the application.
            
            See: https://docs.python.org/2/library/os.html
        '''
        for key in self.defaults:
            environment_variable = "%s_%s" % (self.application_name.upper(), key.upper())
            environment_value = os.environ.get(environment_variable)
            if environment_value:
                setattr(self, key, environment_value)


    def apply_configuration_from_file(self, config_file_path):
        ''' Read application configuration variables from a .conf file.
            Unassigned variables are set to their default values 
            or None if no default is specified at init time.
            The variables are found in a section named by the application.
        
            see: https://docs.python.org/2/library/configparser.html
        '''
        none_defaults = {}
        
        # defaults are set in environment
        # they are only overriden by the config file if present
        for key in self.defaults:
            none_defaults[key] = None

        logging.info("none_defaults: %s" % (none_defaults))
            
        config = None
        
        try:
            config = ConfigParser(defaults=none_defaults, 
                                  allow_no_value=True)
        except:
            logging.warn("This python installation does not support configuration defaults.")
            config = ConfigParser()
    
        config.read(config_file_path)
                    
        for key in self.defaults:
            try:
                file_value = config.get(self.application_name, key)
                if file_value:
                    logging.info("setting %s to %s" % (key, file_value))
                    setattr(self, key, file_value)
            except:
                logging.info("Configuration option not specified: %s" %
                             (key))


        return config
