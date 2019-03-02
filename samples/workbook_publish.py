####
# This script demonstrates how to use the Tableau Server Client
# to publish a workbook to a Tableau server. It will publish
# a specified workbook to the 'default' project of the given server.
#
# Note: The REST API publish process cannot automatically include
# extracts or other resources that the workbook uses. Therefore,
# a .twb file with data from a local computer cannot be published,
# unless packaged into a .twbx file.
#
# For more information, refer to the documentations on 'Publish Workbook'
# (https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm)
#
# To run the script, you must have installed Python 2.7.X or 3.3 and later.
####

import argparse
import logging

import tableauserverclient as TSC
from tableauserverclient.server import Workbooks


def main():

    parser = argparse.ArgumentParser(description='Publish a workbook to server.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--project', default=None)
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('-p', '--password', default=None)
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('workbook', help='one or more workbooks to publish', nargs='+')

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    tableau_auth = TSC.TableauAuth(args.username, args.password)
    server = TSC.Server(args.server)

    overwrite_true = TSC.Server.PublishMode.Overwrite

    with server.auth.sign_in(tableau_auth):

        server.use_server_version()

        all_projects, _ = server.projects.get()
        project = next((project for project in all_projects if project.name == args.project), None)

        if project is None:
            error = "project {0} can not be found".format(args.project)
            raise LookupError(error)

        for wb in args.workbook:
            new_workbook = TSC.WorkbookItem(project.id)
            new_workbook = server.workbooks.publish(new_workbook,
                                                    wb,
                                                    overwrite_true)
            print("workbook published ID: {0}".format(new_workbook.id))


if __name__ == '__main__':
    main()
