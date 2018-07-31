####
# To run the script, you must have installed Python 2.7.X or 3.3 and later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='List project details available on a server')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--site', '-S', default=None)
    parser.add_argument('-p', default=None)

    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    parser.add_argument('project', help='one or more projects to list', nargs='+')

    args = parser.parse_args()

    if args.p is None:
        password = getpass.getpass("Password: ")
    else:
        password = args.p

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)

    with server.auth.sign_in(tableau_auth):
        # Use highest Server REST API version available
        server.use_server_version()

        for p in args.project:
            filter_project_name = p
            options = TSC.RequestOptions()

            options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                          TSC.RequestOptions.Operator.Equals,
                                          filter_project_name))

            filtered_projects, _ = server.projects.get(req_options=options)
            # Result can either be a matching project or an empty list
            if filtered_projects:
                project = filtered_projects.pop()
            else:
                error = "No project named '{}' found".format(filter_project_name)
                print(error)

            #server.projects.populate_permissions(project)
            print("{0}: {1}".format(project.name, project.content_permissions))
            print("==================================================")

            userOptions = TSC.UserRequestOptions(details=TSC.UserRequestOptions.Details.All)
            users_site, _ = server.users.get(userOptions)
            users = dict([(u.id, u) for u in users_site])

            groups, _ = server.groups.get()
            for g in groups:
                print("group: {0}".format(g.name))
                server.groups.populate_users(g)
                for user in g.users:
                    print("{0} ({1}): {2}, {3}".format(users[user.id].name, users[user.id].site_role, users[user.id].fullname, users[user.id].email))
                print("--------------------------------------------------")
            print("==================================================")

            # for c in project.permissions.grantee_capabilities:
            #     #print("{0}: {1}, {2}".format(c.grantee_id, c.grantee_type, c.capabilities))
            #     if c.grantee_type == 'group':
            #         group = [g for g in groups if g.id == c.grantee_id].pop()
            #         print("{0}: {1}".format(group.name, c.capabilities))
            #     if c.grantee_type == 'user':
            #         print("{0}: {1}".format(users[c.grantee_id].name, c.capabilities))
            # print("==================================================")


if __name__ == '__main__':
    main()
