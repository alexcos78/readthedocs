# readthedocs

1. [File change list](#file-change-list)
2. [Prerequisiti](#prerequisiti)
    * [Certificati e posizione](#certificati-e-posizione)
    * [Install docker and docker compose](#install-docker-and-docker-compose)
    * [Deploy proxy](#deploy-proxy)
3. [Install and configure RTD](#install-and-configure-rtd)
   - [RTD file modification](#rtd-file-modification)
   - [LDAP support](#ldap-support)
   - [Hide external integration support](#hide-external-integration-support)
   - [Hide sign up](#hide-sign-up)
   - [Modify header](#modify-header)
4. [Configure systemd and start the service](#configure-systemd-and-start-the-service)

## File change list
```
./readthedocs.org/readthedocs/settings/base.py
./readthedocs.org/readthedocs/settings/dev.py
./readthedocs/redirects/utils.py
./readthedocs/proxito/urls.py
./readthedocs/templates/socialaccount/snippets/provider_list.html
./readthedocs/templates/projects/integration_webhook_detail.html
./readthedocs/templates/projects/project_import.html
./readthedocs/templates/projects/project_dashboard.html
./readthedocs/templates/projects/project_dashboard_base.html
./readthedocs/templates/core/home-header.html
./readthedocs/templates/core/project_bar_base.html
./readthedocs/templates/account/login.html
./readthedocs/projects/models.py
./readthedocs/api/v2/templates/restapi/footer.html
```


## Prerequisiti
Environment Ubuntu 18.04

### Certificati e posizione
```
root@guides-infncloud:~# ls certs/
guides-tb.cloud.cnaf.infn.it.crt  guides-tb.cloud.cnaf.infn.it.key
chmod 440 guides-tb.cloud.cnaf.infn.it.key
chmod 600 guides-tb.cloud.cnaf.infn.it.key
```

### Install docker and Docker-compose

#### Install docker
https://docs.docker.com/engine/install/ubuntu/
```
apt-get update
apt-get upgrade
apt-get install git
apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

apt-get update
apt-get install docker.io
docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
0e03bdcc26d7: Pull complete                                                                                                                                                                                    Digest: sha256:8e3114318a995a1ee497790535e7b88365222a21771ae7e53687ad76563e8e76
Status: Downloaded newer image for hello-world:latest
Hello from Docker!
```

#### Install docker-compose
https://docs.docker.com/compose/install/
```
curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose

ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

docker-compose --version
docker-compose version 1.25.5, build 8a1c60f6
```


### Deploy proxy
```
mkdir proxy/etc
mkdir proxy/cert
cp /root/certs/guides-tb.cloud.cnaf.infn.it.crt  /root/proxy/cert/hostcert.pem  
cp /root/certs/guides-tb.cloud.cnaf.infn.it.key /root/proxy/cert/host.key
```
```
cat proxy/etc/nginx.conf
worker_processes 1;
events { worker_connections 1024; }
http {
    sendfile on;
server {
        listen 443 ssl http2 default_server;
        listen [::]:443 ssl http2 default_server;
        server_name guides-tb.cloud.cnaf.infn.it;
        ssl_certificate     /opt/cert/hostcert.pem;
        ssl_certificate_key /opt/cert/host.key;
        ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers         HIGH:!aNULL:!MD5;
  location / {
    proxy_read_timeout      600;
    proxy_connect_timeout   159s;
    proxy_send_timeout      600;
    proxy_pass              http://guides-tb.cloud.cnaf.infn.it:8000/;
    proxy_set_header        Host $host;
    proxy_set_header        X-Real-IP $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Proto https;
    proxy_redirect          http:// https://;
   }
}
}
```
```
cat proxy/docker-compose.yml
---
version: "3"
services:
  proxy:
    image: nginx:alpine
    container_name: proxy
    volumes:
      - /root/proxy/etc:/etc/nginx/:ro
      - /root/proxy/cert:/opt/cert:ro
    ports:
      - 443:443
    restart: unless-stopped
```
```
cd /root/proxy
docker-compose up –d
# docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                                  PORTS               NAMES
dee0c8d0cb9f        nginx:alpine        "nginx -g 'daemon of…"   5 seconds ago       Restarting (1) Less than a second ago                       proxy
```


## Install and configure RTD

https://docs.readthedocs.io/en/stable/development/install.html
```
apt-get install virtualenv

apt-get install build-essential
apt-get install python-dev python-pip python-setuptools
apt-get install python3-dev python3-pip python3-setuptools
apt-get install libxml2-dev libxslt1-dev zlib1g-dev
apt-get install redis-server

git clone --recurse-submodules https://github.com/readthedocs/readthedocs.org.git

cd readthedocs.org

git checkout 8f9cb194c872419caf4cbe02403270c9901b22ed

virtualenv --python=python3 venv
source venv/bin/activate

pip install -r requirements.txt
apt-get install latexmk
apt-get -y install texlive-latex-recommended texlive-pictures texlive-latex-extra


python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py loaddata test_data
```


### RTD file modification
Refer to the RTD file changes list above

```
cat readthedocs/doc_builder/python_environments.py

        self.build_env.run(
            self.config.python_interpreter,
            '-mvirtualenv',
#INFNClOUD Commented
            #site_packages,

            # This is removed because of the pip breakage,
            # it was sometimes installing pip 20.0 which broke everything
            # https://github.com/readthedocs/readthedocs.org/issues/6585
            # '--no-download',
            env_path,
            # Don't use virtualenv bin that doesn't exist yet
            bin_path=None,
            # Don't use the project's root, some config files can interfere
            cwd='$HOME',
```
```
cat readthedocs/settings/dev.py


   PRODUCTION_DOMAIN = "guides-tb.cloud.cnaf.infn.it"

    SLUMBER_USERNAME = 'test'
    SLUMBER_PASSWORD = 'test'  # noqa: ignore dodgy check
    SLUMBER_API_HOST = 'http://guides-tb.cloud.cnaf.infn.it'
    PUBLIC_API_URL = 'http://guides-tb.cloud.cnaf.infn.it'
```
```
cat readthedocs/settings/base.py

#    PRODUCTION_DOMAIN = 'readthedocs.org'
    PRODUCTION_DOMAIN = 'guides-tb.cloud.cnaf.infn.it'
#    PUBLIC_DOMAIN = None
    PUBLIC_DOMAIN = 'guides-tb.cloud.cnaf.infn.it'
#    PUBLIC_DOMAIN_USES_HTTPS = False
    PUBLIC_DOMAIN_USES_HTTPS = True

    DOCKER_IMAGE_SETTINGS = {
        # A large number of users still have this pinned in their config file.
        # We must have documented it at some point.
        'readthedocs/build:2.0': {
            'python': {
                'supported_versions': [2, 2.7, 3, 3.5],
                'default_version': {
                    2: 2.7,
                    3: 3.6,
                },
            },
        },
        'readthedocs/build:4.0': {
            'python': {
                'supported_versions': [2, 2.7, 3, 3.5, 3.6, 3.7],
                'default_version': {
                    2: 2.7,
                    3: 3.6,
                },
            },
        },
        'readthedocs/build:5.0': {
            'python': {
                'supported_versions': [2, 2.7, 3, 3.5, 3.6, 3.7, 'pypy3.5'],
                'default_version': {
                    2: 2.7,
                    3: 3.6,
                },
            },
        },
        'readthedocs/build:6.0': {
            'python': {
                'supported_versions': [2, 2.7, 3, 3.5, 3.6, 3.7, 3.8, 'pypy3.5'],
                'default_version': {
                    2: 2.7,
                    3: 3.6,
                },
            },
        },
        'readthedocs/build:7.0': {
            'python': {
                'supported_versions': [2, 2.7, 3, 3.5, 3.6, 3.7, 3.8, 'pypy3.5'],
                'default_version': {
                    2: 2.7,
                    3: 3.6,
                },
            },
        },
    }
```




### LDAP support
Refer to the RTD file changes list above

```
# apt-get install libsasl2-dev libldap2-dev libssl-dev 
# apt-get install python3.6-dev
#find / -iname python.h
/usr/include/python3.6m/Python.h
```
```
# pip install django-auth-ldap
Collecting django-auth-ldap
…
Successfully built python-ldap
Installing collected packages: python-ldap, django-auth-ldap
Successfully installed django-auth-ldap-2.1.1 python-ldap-3.2.0
```
```
# vim /root/readthedocs.org/readthedocs/settings/base.py

#######LDAP import

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

#######LDAP params

    AUTH_LDAP_SERVER_URI = "ldaps://ds.infn.it"
    AUTH_LDAP_BIND_DN = "..."
    AUTH_LDAP_BIND_PASSWORD = "..."
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        "ou=People,dc=infn,dc=it", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
    )

########LDAP backend

    AUTHENTICATION_BACKENDS = (
        # Needed to login by username in Django admin, regardless of `allauth`
        'django.contrib.auth.backends.ModelBackend',
        # `allauth` specific authentication methods, such as login by e-mail
        'allauth.account.auth_backends.AuthenticationBackend',
########LDAP
        'django_auth_ldap.backend.LDAPBackend'
    )
```





### Hide external integration support
```
(venv) root@guides:~/readthedocs.org/readthedocs/templates/socialaccount/snippets# cat provider_list.html
{% load socialaccount %}
{% load i18n %}

{% get_providers as socialaccount_providers %}
{% for provider in socialaccount_providers %}
  {% if provider.id == 'github' %}
    <li>
      <a title="{{ provider.name }}"
         class="socialaccount-provider {{ provider.id }} button"
         href="{% provider_login_url provider.id process=process scope=scope auth_params=auth_params next=next %}"
         >
         {% blocktrans trimmed with provider_name=provider.name verbiage=verbiage|default:'Connect to' %}
           {{ verbiage }} {{ provider_name }}
         {% endblocktrans %}
      </a>
    </li>
  {% endif %}
{% endfor %}
```

### Hide sign up
```
root@guides:~/readthedocs.org# cat readthedocs/templates/account/login.html_costa
{% extends "account/base.html" %}
{% load i18n %}
{% load account %}
{% block head_title %}{% trans "Sign In" %}{% endblock %}
{% block body_class %}login-page{% endblock %}
{% block content %}
<h1>{% trans "Sign In with LDAP (testing)" %}</h1>
<!-- <p><small>{% blocktrans trimmed %}If you have not created an account yet, then please -->
<!-- <a href="{{ signup_url }}">sign up</a> first.{% endblocktrans %}</small></p> -->
<form class="login" method="POST" action="{% url "account_login" %}">
  {% csrf_token %}
  {{ form.as_p }}
  {% if redirect_field_value %}
  <input type="hidden" name="{{ redirect_field_name }}" value="{{ redirect_field_value }}" />
  {% endif %}
  <button class="primaryAction" type="submit">{% trans "Sign In" %}</button>
<!--  {% url 'account_reset_password' as password_reset_url %} -->
<!--  <p> -->
<!--    <small>{% blocktrans trimmed %}If you forgot your password, <a href="{{ password_reset_url }}">reset it.</a>{% endblocktrans %}</small> -->
<!--  </p> -->
</form>
<h3>{% trans 'Or' %}</h3>
<div class="clearfix">
  <ul class="socialaccount_providers">
    {% include "socialaccount/snippets/provider_list.html" with process="login" next=request.GET.next verbiage="Sign in with" %}
  </ul>
</div>
{% endblock content %}
```


### Modify header
```
root@guides:~/readthedocs.org# cat  readthedocs/templates/core/home-header.html_costa
{% load i18n %}
    <!-- BEGIN header-->
    <div id="home-header">
      <div class="wrapper">
        <!-- BEGIN header title-->
        <div class="home-header-title">
          <h1>Read the Docs @ INFN CLOUD</h1>
          <p class="tagline">{% trans "Create, host, and browse documentation specific for INFN CLOUD." %}</p>
        </div>
        <!-- END header title -->
        <!-- BEGIN header links-->
        <div class="home-header-links">
          {% comment %}Translators: Note, the full sentence goes 'Sign up' 'or' 'Log in'. But unfortunately the three bits have to be separate.{% endcomment %}
          <a class="login" href="{% url "account_login" %}">{% trans "Log in" %}</a>
          <!-- <div class="login-box"> -->
          <!--  <p>{% trans "or" %} <a class="login" href="{% url "account_login" %}">{% trans "Log in" %}</a></p> -->
         <!-- </div> -->
        </div>
        <!-- END header links -->
      </div>
    </div>
    <!-- END header-->
```


## Configure systemd and start the service

```
# cat /etc/systemd/system/readthedocs.service
[Unit]
Description=RTD Daemon
[Service]
Type=simple
ExecStart=/root/readthedocs.org/RTD.sh
#Restart=on-failure
# Time to wait before forcefully stopped.
TimeoutStopSec=300
[Install]
WantedBy=multi-user.target
```
```
# cat /root/readthedocs.org/RTD.sh
#!/bin/bash
cd /root/readthedocs.org
export HOME=/root
PROFILE=$HOME/readthedocs.org/venv/bin/activate
source $PROFILE
python manage.py runserver 0.0.0.0:8000
```
```
chmod +x /root/readthedocs.org/RTD.sh
```
```
systemctl start readthedocs.service
systemctl status readthedocs.service
systemctl enable readthedocs.service
```

