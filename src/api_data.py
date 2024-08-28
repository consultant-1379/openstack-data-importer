"""Functions to get data from Meteo API and update Capacity Planner."""

import logging
import argparse
import requests
import capacity_planner

LOG = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def main():
    """Main function to import, update, or delete Capacity Planner data."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--capacity-planner-base-url',
        help="""This is the url to the capacity planner
        """,
        required=True
    )
    parser.add_argument(
        '--default-team-name',
        help="""This is the default team to assign new projects to,
        if project name doesn't match existing teams
        """,
        required=True
    )
    parser.add_argument(
        '--default-deployment-type-name',
        help="""This is the default deployment type to assign new projects to
        """,
        required=True
    )
    parser.add_argument(
        '--command-to-run',
        help="""This is the command to run, options are create, update, and delete
        """,
        required=True
    )

    args = parser.parse_args()

    LOG.info("Initialising Capacity Planner")
    cap = {"base_url": args.capacity_planner_base_url,
           "default_team_name": args.default_team_name,
           "default_deployment_type_name": args.default_deployment_type_name}
    cap_planner = capacity_planner.CapacityPlanner(cap)

    pods_list = get_cloud_data()
    projects_list = get_project_data()
    if args.command_to_run == "create":
        upload_cap_planner_data(cap_planner, pods_list, projects_list)
    elif args.command_to_run == "update":
        update_cap_planner_data(cap_planner, projects_list)
    elif args.command_to_run == "delete":
        delete_cap_planner_data(cap_planner)
    else:
        LOG.error("Unknown command, options are create, update, or delete")


def get_project_data():
    """Get project data from Meteo."""
    LOG.info("Getting project data from Meteo")
    projects_api = requests.get("http://10.45.207.10/typhoon/get-project-list-api/")
    projects_data = projects_api.json()
    project_list = projects_data['projects']
    return project_list


def get_cloud_data():
    """Get cloud data from Meteo."""
    LOG.info("Getting cloud data from Meteo")
    pods_api = requests.get("http://10.45.207.10/typhoon/get-clouds-info-api/")
    pods_data = pods_api.json()
    pods_list = pods_data['clouds']
    return pods_list


def get_pod_id(cap_planner, pod_name):
    """
    Get ID of a pod in Capacity Planner.

    Returns a string.
    """
    pod_id = ""
    pods = cap_planner.execute_cap_get_rest_call(
        '/api/pods/'
    )
    for pod in pods:
        if pod['name'] == pod_name:
            pod_id = pod["_id"]
    return pod_id


def get_deployment_type_id(cap_planner, deployment_type_name):
    """
    Get ID of a deployment type in Capacity Planner.

    Returns a string.
    """
    deployment_type_id = ""
    deployment_types = cap_planner.execute_cap_get_rest_call(
        '/api/deploymenttypes/'
    )
    for dep_type in deployment_types:
        if dep_type["name"] == deployment_type_name:
            deployment_type_id = dep_type["_id"]
    return deployment_type_id


def get_deployment_type_name(cap_planner, project_id):
    """
    Get name of a deployment type in Capacity Planner.

    Returns a string.
    """
    deployment_type_id = ""
    projects = get_project_list(cap_planner)
    for project in projects:
        if project["_id"] == project_id:
            deployment_type_id = project["deploymenttype_id"]
    deployment_type_name = ""
    deployment_types = cap_planner.execute_cap_get_rest_call(
        '/api/deploymenttypes/'
    )
    for dep_type in deployment_types:
        if dep_type["_id"] == deployment_type_id:
            deployment_type_name = dep_type["name"]
    return deployment_type_name


def get_team_name(project):
    """
    Get team name based on OpenStack Project name or team name stored in Meteo.

    Returns a string.
    """
    name = project.get('team')
    if name == "":
        full_name = project.get("project_name")
        name = full_name.rsplit("_", 1)[0]
    return name


def get_team_id(cap_planner, team_name):
    """
    Get ID of a team already in Capacity Planner.

    Returns a string.
    """
    team_id = ""
    teams = cap_planner.execute_cap_get_rest_call(
        '/api/teams/'
    )
    for team in teams:
        if team['name'] == team_name:
            team_id = team["_id"]
    return team_id


def get_team_list(cap_planner):
    """
    Get list of teams in Capacity Planner.

    Returns a list of dictionary objects.
    """
    team_list = []
    teams = cap_planner.execute_cap_get_rest_call(
        '/api/teams/'
    )
    for team in teams:
        team_list.append(team['name'])
    return team_list


def get_project_list(cap_planner):
    """
    Get a list of projects in Capacity Planner.

    Returns a list of dictionary objects.
    """
    project_list = []
    projects = cap_planner.execute_cap_get_rest_call(
        '/api/projects/'
    )
    for project in projects:
        project_list.append(project)
    return project_list


def get_project_id(cap_planner, project_name, pod_id):
    """
    Get the ID of a project in Capacity Planner.

    Returns a string.
    """
    project_id = ""
    projects = get_project_list(cap_planner)
    for project in projects:
        if project.get("name") == project_name and project.get("pod_id") == pod_id:
            project_id = project.get("_id")
    return project_id


def post_team(cap_planner, name):
    """Use a post command to add a team name to Capacity Planner."""
    item = '{"name": "' + name + '"}'
    cap_planner.execute_cap_post_rest_call(
        '/api/teams/',
        item
    )


def create_teams(cap_planner, project_list):
    """Create a list of all teams from Meteo in Capacity Planner."""
    project_set = set()
    for project in project_list:
        team_name = get_team_name(project)
        project_set.add(team_name)
    for name in project_set:
        post_team(cap_planner, name)


def delete_team(cap_planner, team_name):
    """Delete a team from Capacity Planner."""
    team_list = cap_planner.execute_cap_get_rest_call(
        '/api/teams/'
    )
    for team in team_list:
        if team_name == team.get("name"):
            team_id = team.get("_id")
            del_item = '/api/teams/' + team_id
            cap_planner.execute_cap_delete_rest_call(
                del_item
            )


def delete_teams(cap_planner):
    """Delete all teams from Capacity Planner."""
    team_list = cap_planner.execute_cap_get_rest_call(
        '/api/teams/'
    )
    for team in team_list:
        team_id = team.get("_id")
        del_item = '/api/teams/' + team_id
        cap_planner.execute_cap_delete_rest_call(
            del_item
        )


def delete_pods(cap_planner):
    """Delete all pods from Capacity Planner."""
    pods = cap_planner.execute_cap_get_rest_call(
        '/api/pods'
    )
    for pod in pods:
        pod_id = pod.get("_id")
        del_item = '/api/pods/' + pod_id
        cap_planner.execute_cap_delete_rest_call(
            del_item
        )


def delete_projects(cap_planner):
    """Delete all projects from Capacity Planner."""
    projects = cap_planner.execute_cap_get_rest_call(
        '/api/projects/'
    )
    for project in projects:
        project_id = project.get("_id")
        del_item = '/api/projects/' + project_id
        cap_planner.execute_cap_delete_rest_call(
            del_item
        )


def delete_project(cap_planner, project_name, pod_id):
    """Delete all projects from Capacity Planner."""
    projects = cap_planner.execute_cap_get_rest_call(
        '/api/projects/'
    )
    for project in projects:
        if project_name == project.get("name") and pod_id == project.get("pod_id"):
            project_id = project.get("_id")
            del_item = '/api/projects/' + project_id
            cap_planner.execute_cap_delete_rest_call(
                del_item
            )


def create_pods(cap_planner, pods_list):
    """Create all pods from Meteo data in Capacity Planner."""
    project = "Cap_Plan_Viewer"
    username = "cap_plan_user"
    password = "passwd123"
    for pod in pods_list:
        item = '{"name": "cloud' + pod.get("cloud_name") + \
               '", "authUrl": "' + pod.get("auth_url") + \
               '", "project": "' + project + \
               '", "username": "' + username + \
               '", "password": "' + password + \
               '", "cpu": ' + pod.get("total_cpu") + \
               ', "memory_mb": ' + pod.get("total_ram") + \
               ', "cinder_gb": ' + pod.get("total_cinder_storage") + \
               ', "cinder_iops": ' + pod.get("cinder_iops") + \
               ', "enfs_gb": ' + pod.get("total_enfs_storage") + \
               ', "enfs_iops": ' + pod.get("total_enfs_iops") + \
               ', "cpu_contention_ratio": ' + pod.get("cpu_ratio") + \
               '}'
        cap_planner.execute_cap_post_rest_call(
            '/api/pods/',
            item
        )


def create_projects(cap_planner, project_list):
    """Create all projects from Meteo data in Capacity Planner."""
    for project in project_list:
        project_name = project.get("project_name")
        pod = project.get("cloud")
        team_name = get_team_name(project)
        cpu = project.get("allocated_cpu")
        memory_mb = project.get("allocated_ram")
        cinder_gb = project.get("allocated_storage")
        deployment_type = "5K"
        team_id = get_team_id(cap_planner, team_name)
        deployment_type_id = get_deployment_type_id(cap_planner, deployment_type)
        pod_id = get_pod_id(cap_planner, "cloud" + str(pod))
        item = '{"pod_id": "' + pod_id + \
               '", "team_id": "' + team_id + \
               '", "deploymenttype_id": "' + deployment_type_id + \
               '", "name": "' + project_name + \
               '", "cpu": ' + cpu + \
               ', "memory_mb": ' + memory_mb + \
               ', "cinder_gb": ' + cinder_gb + \
               '}'

        cap_planner.execute_cap_post_rest_call(
            '/api/projects/',
            item
        )


def update_projects(cap_planner, project_list):
    """Update projects from Meteo data in Capacity Planner."""
    for project in project_list:
        project_name = project.get("project_name")
        pod = project.get("cloud")
        team_name = get_team_name(project)
        pod_id = get_pod_id(cap_planner, "cloud" + str(pod))
        project_id = get_project_id(cap_planner, project_name, pod_id)
        deployment_type = get_deployment_type_name(cap_planner, project_id)
        item = '{"pod_id": "' + pod_id + \
               '", "team_id": "' + get_team_id(cap_planner, team_name) + \
               '", "deploymenttype_id": "' + get_deployment_type_id(cap_planner, deployment_type) +\
               '", "name": "' + project.get("project_name") + \
               '", "cpu": ' + project.get("allocated_cpu") + \
               ', "memory_mb": ' + project.get("allocated_ram") + \
               ', "cinder_gb": ' + project.get("allocated_storage") + \
               '}'
        cap_planner.execute_cap_put_rest_call(
            '/api/projects/' + project_id,
            item
        )


def delete_cap_planner_data(cap_planner):
    """
    Delete all Projects, Pods, and Teams from Capacity Planner.

    Doesn't include Deployment Types.
    """
    LOG.info("Deleting all projects from Capacity Planner")
    delete_projects(cap_planner)

    LOG.info("Deleting all teams from Capacity Planner")
    delete_teams(cap_planner)

    LOG.info("Deleting all pods from Capacity Planner")
    delete_pods(cap_planner)


def upload_cap_planner_data(cap_planner, pods_list, projects_list):
    """
    Upload all Pods, Teams, and Projects to Capacity Planner.

    Doesn't include Deployment Types.
    """
    LOG.info("Creating all pods in Capacity Planner")
    create_pods(cap_planner, pods_list)

    LOG.info("Creating all teams in Capacity Planner")
    create_teams(cap_planner, projects_list)

    LOG.info("Creating all projects in Capacity Planner")
    create_projects(cap_planner, projects_list)


def update_cap_planner_data(cap_planner, projects_list):
    """
    Update Teams and Projects in Capacity Planner.

    Doesn't include Deployment Types.
    """
    LOG.info("Adding new teams")
    add_new_teams(cap_planner, projects_list)

    LOG.info("Updating projects")
    update_projects_and_teams(cap_planner, projects_list)

    LOG.info("Removing unused projects")
    remove_unused_projects(cap_planner, projects_list)

    LOG.info("Removing unused teams")
    remove_unused_teams(cap_planner, projects_list)


def update_projects_and_teams(cap_planner, project_list):
    """Update existing projects and add new projects to Capacity Planner."""
    existing_projects_list = []
    new_projects_list = []
    projects_to_create = []
    projects_to_update = []
    existing_projects = get_project_list(cap_planner)
    for project in existing_projects:
        existing_projects_list.append(project.get("name"))
    for project in project_list:
        new_projects_list.append(project)
    for new_project in new_projects_list:
        if new_project.get('project_name') not in existing_projects_list:
            projects_to_create.append(new_project)
        else:
            projects_to_update.append(new_project)
    for project in projects_to_create:
        existing_teams = get_team_list(cap_planner)
        team_name = get_team_name(project)
        if team_name not in existing_teams:
            post_team(cap_planner, team_name)
    LOG.info("Creating new projects in Capacity Planner")
    create_projects(cap_planner, projects_to_create)
    LOG.info("Updating projects in Capacity Planner")
    update_projects(cap_planner, projects_to_update)


def add_new_teams(cap_planner, project_list):
    """Add any new teams to Capacity Planner."""
    cap_plan_team_list = get_team_list(cap_planner)
    opstk_team_list = []
    teams_to_add = set()
    for project in project_list:
        team_name = get_team_name(project)
        opstk_team_list.append(team_name)
    for team in opstk_team_list:
        if team not in cap_plan_team_list:
            teams_to_add.add(team)
    for team in teams_to_add:
        post_team(cap_planner, team)


def remove_unused_teams(cap_planner, project_list):
    """Remove unused teams from Capacity Planner."""
    cap_plan_team_list = get_team_list(cap_planner)
    opstk_team_list = []
    teams_to_remove = []
    for project in project_list:
        team_name = get_team_name(project)
        opstk_team_list.append(team_name)
    for team in cap_plan_team_list:
        if team not in opstk_team_list:
            teams_to_remove.append(team)
    for team_name in teams_to_remove:
        delete_team(cap_planner, team_name)


def remove_unused_projects(cap_planner, project_list):
    """Remove unused projects from Capacity Planner."""
    cap_plan_project_list = get_project_list(cap_planner)
    opstk_project_list = project_list
    for project in cap_plan_project_list:
        for opstk_project in opstk_project_list:
            project_in_opstk = False
            if project["name"] == opstk_project["project_name"]:
                project_in_opstk = True
                break
        if not project_in_opstk:
            del_item = '/api/projects/' + project.get("_id")
            cap_planner.execute_cap_delete_rest_call(
                del_item
            )


if __name__ == "__main__":
    main()
