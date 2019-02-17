import argparse
import getpass
import logging

import tableauserverclient as TSC
from tableaudocumentapi import Workbook


def main():
    parser = argparse.ArgumentParser(description='Connect and publish a workbook to a server.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--password', '-p', required=True, help='password for the user')
    parser.add_argument('--dest', '-D', required=True, help='destination server address')
    parser.add_argument('-U', required=True, help='username to sign into destination server')
    parser.add_argument('-P', required=True, help='password for the user on the destination server')
    parser.add_argument('--source', '-S', default=None)
    parser.add_argument('--target', '-T', default=None)
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('workbook', help='one or more workbooks to publish', nargs='+')

    args = parser.parse_args()

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Step 1: Sign in to server.
    server, server_auth = connect(args.server, args.username, args.password)
    dest, dest_auth = connect(args.dest, args.U, args.P)

    overwrite_true = TSC.Server.PublishMode.Overwrite

    with server.auth.sign_in(server_auth) and dest.auth.sign_in(dest_auth):

        # Step 2: Get the project on server.
        source = filter_project(args.source, server)
        target = filter_project(args.target, dest)
        print("source: {0}[{1}]".format(server.baseurl, source.name))
        print("destination: {0}[{1}]".format(dest.baseurl, target.name))

        # Step 4: If project is found, form a new workbook item and publish.
        if source is not None and target is not None:
            # Step 3: Build a list of datasources.
            ds_source = extract_ds(server, source)
            ds_target = extract_ds(dest, target)
            # Step 4: Form a new workbook item and publish.
            for wb in args.workbook:
                pub = Workbook(wb)
                for ds in pub.datasources:
                    print("{0}, {1}".format(ds.caption, ds.name))
                    if len(ds.connections) == 1:
                        ds.connections[0].dbname = datasources[ds.name].content_url
                new_workbook = TSC.WorkbookItem(project.id)
                new_workbook = server.workbooks.publish(new_workbook,
                                                        wb,
                                                        overwrite_true)
                print("workbook published ID: {0}".format(new_workbook.id))


def extract_ds(server, project):
    datasources = {}
    for ds in TSC.Pager(server.datasources.get):
        if ds.project_name == project.name:
            server.datasources.populate_connections(ds)
            datasources[ds.name] = ds
            print("{0}, {1}".format(ds.name, ds.name))
    return datasources


def connect(host, username, password):
    server_auth = TSC.TableauAuth(username, password)
    server = TSC.Server(host)
    server.use_server_version()
    return server, server_auth


def filter_project(filter_project_name, server):
    options = TSC.RequestOptions()
    options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                  TSC.RequestOptions.Operator.Equals,
                                  filter_project_name))
    filtered_projects, _ = server.projects.get(req_options=options)
    if filtered_projects:
        project = filtered_projects.pop()
        return project
    else:
        error = "no project named '{0}' found".format(filter_project_name)
        raise LookupError(error)
    return None


if __name__ == '__main__':
    main()
