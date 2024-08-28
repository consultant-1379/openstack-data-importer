"""This file contains logic relating to the capacity planner."""

import urlparse
import logging
import json
import requests

LOG = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class CapacityPlanner(object):
    """Represents a capacity planner instance."""

    def __init__(self, kwargs):
        """Initialize a capacity planner object."""
        self.base_url = kwargs.pop('base_url')
        self.default_deployment_type_id = self.get_deployment_type_id(
            deployment_type_name=kwargs.pop('default_deployment_type_name')
        )
        self.cap_teams = self.execute_cap_get_rest_call('/api/teams/')
        self.default_team_id = self.get_team_id(
            team_name=kwargs.pop('default_team_name')
        )
        self.cap_pods = self.execute_cap_get_rest_call('/api/pods/')
        self.cap_projects = self.execute_cap_get_rest_call('/api/projects/')

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

    def get_team_id(self, team_name):
        """
        Return the id of the given team.

        Return the id of the given team from the capacity planner
        and create it if its not there
        """
        team_name = team_name

        team_id = None
        for team in self.cap_teams:
            if team['name'] == team_name:
                team_id = team['_id']

        if team_id is None:
            LOG.info("Creating default team '" + team_name + "'")
            teams_post_response = self.execute_cap_post_rest_call(
                '/api/teams/',
                json.dumps({'name': team_name})
            )
            team_id = teams_post_response['_id']
        return team_id

    def get_deployment_type_id(self, deployment_type_name):
        """Return the id of the given deployment type name from the capacity planner."""
        deployment_type_name = deployment_type_name

        deployment_types = self.execute_cap_get_rest_call(
            '/api/deploymenttypes/',
            {'q': 'name=' + deployment_type_name}
        )
        if len(deployment_types) == 1:
            return deployment_types[0]['_id']
        else:
            raise RuntimeError(
                "The deployment type name given could not be found in the capacity planner"
            )

    def execute_cap_get_rest_call(self, url_string, payload=None):
        """Return the result of a GET REST call towards the capacity planner."""
        full_url = urlparse.urljoin(self.base_url, url_string)
        LOG.info(
            "Running GET REST call towards the Capacity Planner (%s%s)",
            full_url,
            ' with payload ' + str(payload) if payload else ''
        )
        logging.getLogger("requests").setLevel(logging.WARNING)
        response = requests.get(full_url, params=payload)
        response.raise_for_status()
        LOG.info("REST call completed")
        return response.json()

    def execute_cap_put_rest_call(self, url_string, json_data):
        """Return the result of a PUT REST call towards the capacity planner."""
        full_url = urlparse.urljoin(self.base_url, url_string)
        LOG.info(
            "Running PUT REST call towards the Capacity Planner (%s) with payload %s",
            full_url,
            json_data
        )
        logging.getLogger("requests").setLevel(logging.WARNING)
        headers = {"Content-Type": "application/json"}
        response = requests.put(full_url, data=json_data, headers=headers)
        response.raise_for_status()
        LOG.info("REST call completed")
        return response.json()

    def execute_cap_post_rest_call(self, url_string, json_data):
        """Return the result of a POST REST call towards the capacity planner."""
        full_url = urlparse.urljoin(self.base_url, url_string)
        LOG.info(
            "Running POST REST call towards the Capacity Planner (%s) with payload %s",
            full_url,
            json_data
        )
        logging.getLogger("requests").setLevel(logging.WARNING)
        headers = {"Content-Type": "application/json"}
        response = requests.post(full_url, data=json_data, headers=headers)
        response.raise_for_status()
        LOG.info("REST call completed")
        return response.json()

    def execute_cap_delete_rest_call(self, url_string):
        """Return the result of a DELETE REST call towards the capacity planner."""
        full_url = urlparse.urljoin(self.base_url, url_string)
        LOG.info(
            "Running DELETE REST call towards the Capacity Planner (%s)",
            full_url
        )
        logging.getLogger("requests").setLevel(logging.WARNING)
        headers = {"Content-Type": "application/json"}
        response = requests.delete(full_url, headers=headers)
        response.raise_for_status()
        LOG.info("REST call completed")
        return response.json()
