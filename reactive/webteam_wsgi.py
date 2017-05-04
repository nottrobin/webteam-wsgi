# Core packages
import os
import shutil
import sys
import tarfile

# Third-party packages
from charmhelpers.core.hookenv import config, resource_get, status_set
from charms.reactive import hook, set_state, when


@hook('config-changed')
def update():
    # Copy source code
    resource_path = resource_get('application')

    if not resource_path:
        status_set(
            'blocked',
            'Waiting for "application" resource'
        )
        sys.exit(0)

    status_set(
        'maintenance',
        'Extracting application code'
    )

    tar = tarfile.open(resource_path)
    tar.extractall('/srv/next')
    tar.close()

    if os.path.isdir('/srv/previous'):
        shutil.rmtree('/srv/previous')

    if os.path.isdir('/srv/active'):
        os.rename('/srv/active', '/srv/previous')

    os.rename('/srv/next', '/srv/active')

    set_state('wsgi.application.ready')


@when('wsgi.running')
def set_status():
    build_filepath = '/srv/BUILD_LABEL'
    port = config('port') or 80

    if os.path.exists(build_filepath):
        with open('/srv/BUILD_LABEL') as build_file:
            build_label = build_file.read().strip()

        status_set(
            'active',
            'Build {build_label} running on port {port}'.format(**locals())
        )
