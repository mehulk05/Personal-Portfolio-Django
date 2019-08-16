"""
Fabfile.py
"""


from contextlib import contextmanager as _contextmanager
from fabric.api import run, env, cd, local, puts, task, prefix, sudo
from fabric.colors import green


"""
ENVS
"""


@task
def staging():
    "Set environments as staging"
    env.hostname = 'production'
    env.hosts = ['erickagrazal.com', ]
    env.user = 'deploy'
    env.base_project_name = '/www'
    env.project_name = 'portfolio'
    env.project_folder = '%s/%s/%s' % (env.base_project_name, env.project_name,
                                       env.project_name)
    env.project_venv_name = 'django'
    env.project_git_url = 'git@github.com:ErickAgrazal/portfolio.git'

    env.directory = '%s/%s' % (env.base_project_name, env.project_name)
    env.venv_directory = '%s/%s/%s' % (env.base_project_name,
                                       env.project_name,
                                       env.project_venv_name)
    env.activate = 'source %s/bin/activate' % (env.venv_directory)


@_contextmanager
def virtualenv():
    with cd(env.directory):
        with cd(env.project_name):
            with prefix(env.activate):
                puts(green('Enabling virtualenv'))
                yield


"""
Setup scripts
"""


@task
def set_gunicorn_start_as_executable():
    "Set gunicorn start as executable"
    puts(green("Setting gunicorn_start as executable"))
    run("chmod u+x %s/deploy/%s/gunicorn_start.sh" % (env.project_folder,
                                                      env.hostname))


@task
def set_celery_start_as_executable():
    "Set gunicorn start as executable"
    puts(green("Setting gunicorn_start as executable"))
    run("chmod u+x %s/deploy/%s/celery_start.sh" % (env.project_folder,
                                                    env.hostname))


@task
def create_base_project():
    "Create base project folder"
    puts(green('Creating base project'))
    run("mkdir -p %s/" % (env.directory))


@task
def create_www():
    "Configure permissions on www"
    sudo("mkdir -p %s/" % (env.base_project_name))
    sudo("chown -R %s:www-data %s/" % (env.user, env.base_project_name))
    run("chmod 775 -R %s/" % (env.base_project_name))
    run("chmod g+s -R %s/" % (env.base_project_name))


@task
def create_virtual_env():
    "Create virtual environment"
    with cd(env.directory):
        puts(green('Creating virtualenv'))
        run("virtualenv %s" % (env.project_venv_name))


@task
def clone_project():
    "Clone project"
    with cd(env.directory):
        puts(green('Cloning project'))
        run("git clone %s" % (env.project_git_url))
        with cd(env.project_name):
            set_gunicorn_start_as_executable()
            set_celery_start_as_executable()


@task
def install_requirements():
    "Install requirements"
    with virtualenv():
        puts(green("Installing requirements for %s." % (env.hosts[0])))
        run("pip install --upgrade pip-tools")
        run("export DJANGO_SETTINGS_MODULE="" "
            "&& pip install -r requirements.txt")


@task
def setup():
    """
    Initial setup of the server
    """
    create_www()
    create_base_project()
    clone_project()
    create_virtual_env()
    install_requirements()
    install_supervisor()
    install_nginx()
    with virtualenv():
        puts(green('Setting static files fir'))
        run('ln -s static/ ./staticfiles')


"""
Supervisor config
"""


@task
def update_supervisor_config():
    "Update supervisor config"
    puts(green('Updating supervising config'))
    sudo('cp %s/deploy/%s/gunicorn.conf '
         '/etc/supervisor/conf.d/%s.conf'
         % (env.project_folder, env.hostname, env.project_name))


@task
def install_supervisor():
    "Install Supervisor"
    run('sudo apt-get -y install supervisor')
    with cd(env.directory):
        puts(green('Creating run folder'))
        run('mkdir -p logs')
        run('touch logs/gunicorn-error.log')
        puts(green('Creating run folder'))
        run('mkdir -p run')
        update_supervisor_config()
        start_supervisor()
        update_supervisor()


@task
def enable_supervisor():
    "Enable Supervisor"
    run('sudo systemctl enable supervisor')


@task
def start_supervisor():
    "Star Supervisor"
    run('sudo systemctl start supervisor')


@task
def stop_supervisor():
    "Star Supervisor"
    run('sudo systemctl stop supervisor')


@task
def update_supervisor():
    puts(green('Updating supervisor'))
    update_supervisor_config()
    sudo('supervisorctl reread')
    sudo('supervisorctl update')
    sudo('supervisorctl restart %s' % env.project_name)
    sudo('supervisorctl restart %s-celery' % env.project_name)


"""
NGINX Scripts
"""


@task
def install_nginx():
    puts(green('Installing nginx'))
    sudo('apt-get -y install nginx')
    sudo('ln -s /etc/nginx/sites-available/%s '
         '/etc/nginx/sites-enabled/%s' % (env.project_name, env.project_name))
    sudo('rm /etc/nginx/sites-enabled/default')
    with virtualenv():
        run('ln -s static/ ./staticfiles')


@task
def update_nginx_config():
    "Update supervisor config"
    puts(green('Updating nginx config'))
    sudo('cp %s/deploy/%s/nginx.conf '
         '/etc/nginx/sites-available/%s'
         % (env.project_folder, env.hostname, env.project_name))


@task
def update_nginx():
    puts(green('Updating nginx'))
    update_nginx_config()
    sudo('service nginx restart')


"""
Celery
"""


@task
def update_celery():
    puts(green('Updating celery config'))
    sudo('cp %s/deploy/%s/celery.conf '
         '/etc/supervisor/conf.d/%s-celery.conf'
         % (env.project_folder, env.hostname, env.project_name))


"""
REDIS
"""


@task
def install_redis():
    sudo('apt-get install redis-server')


"""
GIT scripts
"""


@task
def update():
    "Update server content"
    puts(green("Pushing git repository"))
    local("git push")
    with cd(env.directory):
        with cd(env.project_name):
            puts(green("Fetching repository"))
            run('git fetch --all')
            run('git reset --hard origin/master')
            set_gunicorn_start_as_executable()
            set_celery_start_as_executable()
            update_supervisor()
            update_nginx()
            update_celery()
            static()
            migrate()


@task
def deploy():
    update()
    install_requirements()
    update_supervisor()


"""
TOOLS
"""


@task
def omo():
    "Lava mais branco"
    with cd(env.directory):
        with cd(env.project_name):
            run('find -name "*.pyc" -delete')


@task
def gunicorn():
    "Launch gunicorn"
    with virtualenv():
        run('gunicorn src.wsgi:application --bind 0.0.0.0:8001')


"""
Django
"""


@task
def static():
    "Collect Static Files"
    with virtualenv():
        puts(green('Collect static files'))
        run('python manage.py collectstatic -l --noinput')


@task
def migrate():
    "Django Syncdb"
    with virtualenv():
        puts(green('Migrating database'))
        run('python manage.py migrate --settings=%s.settings.%s'
            % (env.project_name, env.hostname))


@task
def shell():
    "Django Shell"
    with virtualenv():
        run('python manage.py shell_plus --ipython --settings=src.settings.%s'
            % (env.hostname))


@task
def dbshell():
    "Django DB Shell"
    with virtualenv():
        run('python manage.py dbshell')


@task
def command(*args):
    """
    Send custom command with args or not. Usage:
    fab command:mycustom,123 or fab command:mycustom
    """
    with virtualenv():
        run('python manage.py ' + " ".join(args))
