from fabric.api import env, run
import fabric.contrib.project as project


env.user = 'www-data'
env.hosts = ['chtoes.li']


def publish():
    base_dir = '/var/www/api.chtoes.li/public'
    project.rsync_project(
        local_dir='app/',
        remote_dir='{base_dir}/app/'.format(base_dir=base_dir),
        exclude=['.*.sw[a-z]', '*.pyc', '__pycache__'],
        delete=True,
    )
    run('touch {base_dir}/touch-reload'.format(base_dir=base_dir))
