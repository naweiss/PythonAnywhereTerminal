#!/usr/bin/env python3
import configargparse
import logging

from event_loop import start_terminal
from session.remote import PythonAnywhereSession


def init_logger(verbose=False):
    logging.basicConfig(
        filename='PythonAnywhere.log',
        filemode='a',
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG if verbose else logging.INFO
    )


def parse_arguments():
    parser = configargparse.ArgumentParser(description='Open a remote console on PythonAnywhere account.')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    base_parser = configargparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--username', help='account username', required=True)
    base_parser.add_argument('--password', help='account password', required=True)
    base_parser.add_argument('-v', '--verbose', dest='verbose', help='verbose logging',
                             action='store_true', default=False)
    base_parser.add_argument('-c', '--config', is_config_file=True, help='config file path')

    execution_parser = subparsers.add_parser('exec', parents=[base_parser], default_config_files=['~/.anywhere.ini'])
    execution_parser.add_argument('--windowed', help='run using curses', action='store_true', default=False)
    execution_parser.add_argument('executable', help='open a new console of the give type', default=None)

    subparsers.add_parser('list', parents=[base_parser], default_config_files=['~/.anywhere.ini'])

    return parser.parse_args()


def main():
    arguments = parse_arguments()
    init_logger(verbose=arguments.verbose)

    with PythonAnywhereSession(username=arguments.username, password=arguments.password) as session:
        if arguments.command == 'list':
            for console in session.iter_consoles():
                print('{}# {}: running {}'.format(console['id'], console['name'], console['executable']))

        elif arguments.command == 'exec':
            consoles = session.iter_consoles(where=lambda console: console['executable'] == arguments.executable)
            console = next(consoles, session.new_console(arguments.executable))
            start_terminal(session_id=session.get_cookie('sessionid'),
                           console_id=console['id'], is_windowed=arguments.windowed)


if __name__ == "__main__":
    main()
