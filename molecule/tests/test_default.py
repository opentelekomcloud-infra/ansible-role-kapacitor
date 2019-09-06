import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.fixture(scope='module')
def kapacitor_user(host):
    ansible_vars = host.ansible.get_variables()
    user = ansible_vars.get('kapacitor_os_user', 'kapacitor')
    group = ansible_vars.get('kapacitor_os_group', 'kapacitor')

    return {'user': user, 'group': group}


@pytest.mark.parametrize('pkg', [
    'podman',
    'firewalld'
    # 'libselinux-python'
])
def test_kapacitor_packages_installed(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_kapacitor_systemd_config(host):
    data = host.file('/etc/systemd/system/kapacitor-service.service')

    assert data.exists
    assert data.user == 'root'
    assert data.group == 'root'


def test_kapacitordb_user(host, kapacitor_user):
    user = host.user(kapacitor_user['user'])
    assert user.group == kapacitor_user['group']


def test_kapacitordb_config(host, kapacitor_user):
    for fname in ['/etc/kapacitor',
                  '/etc/kapacitor/env']:
        data = host.file(fname)

        assert data.exists
        assert data.user == kapacitor_user['user']
        assert data.group == kapacitor_user['group']


@pytest.mark.parametrize('srv', [
    'kapacitor-service',
    'firewalld'
])
def test_kapacitor_running(host, srv):
    service = host.service(srv)

    assert service.is_running
    assert service.is_enabled
