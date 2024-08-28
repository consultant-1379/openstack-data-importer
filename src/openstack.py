"""
This module contains functions relating specifically to openstack.

It contains logic relating to interaction with the openstack clients
"""

import json
import os
import logging
import utils

LOG = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def setup_openstack_env_variables(openstack_env):
    """
    Set required openstack environment variables.

    This function sets the required openstack environment variables
    that are necessary for running openstack cli commands
    """
    os.environ["OS_AUTH_URL"] = openstack_env['os_auth_url']
    os.environ["OS_TENANT_NAME"] = openstack_env['os_project_name']
    os.environ["OS_PROJECT_NAME"] = openstack_env['os_project_name']
    os.environ["OS_USERNAME"] = openstack_env['os_username']
    os.environ["OS_PASSWORD"] = openstack_env['os_password']


def openstack_client_command(**kwargs):
    """Run the openstack client cli command, with the given action and arguments."""
    command_type = kwargs.pop('command_type')
    object_type = kwargs.pop('object_type')
    action = kwargs.pop('action')
    command_requires_region = kwargs.pop('command_requires_region', False)
    arguments = kwargs.pop('arguments')
    return_an_object = kwargs.pop('return_an_object', True)

    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    if command_type == 'openstack':
        command_and_arguments = command_type + " " + object_type + " " + action + " " + arguments
    else:
        command_and_arguments = command_type + " " + object_type + "-" + action + " " + arguments

    if return_an_object and command_type == 'openstack':
        command_and_arguments += " -f json"

    if command_requires_region:
        os.environ["OS_REGION_NAME"] = "RegionOne"
    else:
        if "OS_REGION_NAME" in os.environ:
            del os.environ["OS_REGION_NAME"]

    cli_command_output = utils.run_cli_command(command_and_arguments)
    cli_command_standard_output = cli_command_output['standard_output']

    if return_an_object:
        if command_type != 'openstack':
            output_list = {}
            lines = cli_command_standard_output.split('\n')[3:-2]
            for line in lines:
                line_parts = line.split('|')
                output_list[line_parts[1].strip()] = line_parts[2].strip()
        else:
            output_list = json.loads(cli_command_standard_output)

        return output_list


def get_cinder_pool_details():
    """Run the cinder client cli command, to get details about the available pools."""
    return openstack_client_command(
        command_type="cinder",
        object_type="--os_volume_api_version=2 get",
        action="pools",
        arguments="--detail",
        return_an_object=True
    )


def get_nova_hypervisor_stats():
    """Run the nova client cli command, to get details about the nova hypervisor stats."""
    return openstack_client_command(
        command_type="nova",
        object_type="hypervisor",
        action="stats",
        arguments="",
        return_an_object=True
    )


def get_project_list():
    """Return the list of projects."""
    return openstack_client_command(
        command_type="openstack",
        object_type="project",
        action="list",
        arguments="",
        command_requires_region=True,
        return_an_object=True
    )


def get_project_quotas(**kwargs):
    """Return the quota details for the given project name."""
    project_name = kwargs.pop('project_name', '')

    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)

    return openstack_client_command(
        command_type="openstack",
        object_type="quota",
        action="show",
        arguments=project_name,
        return_an_object=True
    )
