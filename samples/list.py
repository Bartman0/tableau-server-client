####
# This script demonstrates how to list all of the workbooks or datasources
#
# To run the script, you must have installed Python 2.7.X or 3.3 and later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='List out the names and LUIDs for different resource types')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-S', default=None, help='site to log into, do not specify for default site')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--password', '-p', default=None, help='password for the user')

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('resource_type', choices=['workbook', 'datasource', 'view'])

    args = parser.parse_args()

    if args.password is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.password

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password, args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        endpoint = {
            'workbook': server.workbooks,
            'datasource': server.datasources,
            'view': server.views
        }.get(args.resource_type)

        for resource in TSC.Pager(endpoint.get):
            print(resource.id, resource.name, resource.content_url)


if __name__ == '__main__':
    main()
