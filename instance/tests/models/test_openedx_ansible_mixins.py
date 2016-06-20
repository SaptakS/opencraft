# -*- coding: utf-8 -*-
#
# OpenCraft -- tools to aid developing and hosting free software projects
# Copyright (C) 2015-2016 OpenCraft <contact@opencraft.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
OpenEdXAppServer Ansible Mixin - Tests
"""

# Imports #####################################################################

import os
from configparser import ConfigParser
from unittest.mock import patch, call, Mock

from instance.models.mixins.ansible import Playbook
from instance.tests.base import TestCase
from instance.tests.models.factories.openedx_appserver import make_test_appserver
from instance.tests.utils import patch_services


# Tests #######################################################################


class AnsibleAppServerTestCase(TestCase):
    """
    Test cases for AnsibleAppServerMixin models
    """
    @patch_services
    def test_inventory_str(self, mocks):
        """
        Ansible inventory string - should contain the public IP of the AppServer's VM
        """
        mocks.mock_create_server.side_effect = [Mock(id='test-inventory-server'), None]
        mocks.os_server_manager.add_fixture('test-inventory-server', 'openstack/api_server_2_active.json')

        appserver = make_test_appserver()
        appserver.provision()  # This is when the server gets created
        inventory = ConfigParser(allow_no_value=True)
        inventory.read_string(appserver.inventory_str)
        for group in appserver.ansible_groups:
            self.assertEqual(inventory[group].keys(), {'192.168.100.200'})

    @patch_services
    def test_inventory_str_no_server(self, mocks):
        """
        Ansible inventory string - should raise an exception if the server has no public IP
        """
        appserver = make_test_appserver()
        with self.assertRaises(RuntimeError) as context:
            self.assertEqual(appserver.inventory_str, '[app]\n')
        self.assertEqual(str(context.exception), "Cannot prepare to run playbooks when server has no public IP.")

    @patch('instance.models.mixins.ansible.poll_streams')
    @patch('instance.models.openedx_appserver.OpenEdXAppServer.inventory_str')
    @patch('instance.models.mixins.ansible.ansible.run_playbook')
    @patch('instance.models.mixins.ansible.open_repository')
    def test_provisioning(self, mock_open_repo, mock_run_playbook, mock_inventory, mock_poll_streams):
        """
        Test instance provisioning
        """
        appserver = make_test_appserver()
        working_dir = '/cloned/configuration-repo/path'
        mock_open_repo.return_value.__enter__.return_value.working_dir = working_dir

        appserver.run_ansible_playbooks()

        self.assertIn(call(
            requirements_path='{}/requirements.txt'.format(working_dir),
            inventory_str=mock_inventory,
            vars_str=appserver.configuration_settings,
            playbook_path='{}/playbooks'.format(working_dir),
            playbook_name='edx_production.yml',
            username='ubuntu',
        ), mock_run_playbook.mock_calls)

    @patch('instance.models.mixins.ansible.ansible.run_playbook')
    @patch('instance.models.mixins.ansible.AnsibleAppServerMixin.inventory_str')
    def test_run_playbook_logging(self, mock_inventory_str, mock_run_playbook):
        """
        Ensure logging routines are working on _run_playbook method
        """
        stdout_r, stdout_w = os.pipe()
        stderr_r, stderr_w = os.pipe()
        with open(stdout_r, 'rb', buffering=0) as stdout, open(stderr_r, 'rb', buffering=0) as stderr:
            mock_run_playbook.return_value.__enter__.return_value.stdout = stdout
            mock_run_playbook.return_value.__enter__.return_value.stderr = stderr
            mock_run_playbook.return_value.__enter__.return_value.returncode = 0
            os.write(stdout_w, b'Hello\n')
            os.close(stdout_w)
            os.write(stderr_w, b'Hi\n')
            os.close(stderr_w)
            appserver = make_test_appserver()
            playbook = Playbook(source_repo='dummy', playbook_path='dummy', requirements_path='dummy', version='dummy',
                                variables='dummy')
            log, returncode = appserver._run_playbook("/tmp/test/working/dir/", playbook)
            self.assertCountEqual(log, ['Hello', 'Hi'])
            self.assertEqual(returncode, 0)