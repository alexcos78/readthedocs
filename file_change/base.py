# pylint: disable=missing-docstring

import getpass
import os

#costa
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
#costa

from celery.schedules import crontab

from readthedocs.core.settings import Settings


try:
    import readthedocsext  # noqa
    ext = True
except ImportError:
    ext = False


_ = gettext = lambda s: s


class CommunityBaseSettings(Settings):

    """Community base settings, don't use this directly."""

    # Django settings
    SITE_ID = 1
    ROOT_URLCONF = 'readthedocs.urls'
    SUBDOMAIN_URLCONF = 'readthedocs.core.urls.subdomain'
    SINGLE_VERSION_URLCONF = 'readthedocs.core.urls.single_version'
    LOGIN_REDIRECT_URL = '/dashboard/'
    FORCE_WWW = True
    SECRET_KEY = 'replace-this-please'  # noqa
    ATOMIC_REQUESTS = True

    # Debug settings
    DEBUG = True

    # Domains and URLs
#    PRODUCTION_DOMAIN = 'readthedocs.org'
    PRODUCTION_DOMAIN = 'guides-tb.cloud.cnaf.infn.it'
#    PUBLIC_DOMAIN = None
    PUBLIC_DOMAIN = 'guides-tb.cloud.cnaf.infn.it'
#    PUBLIC_DOMAIN_USES_HTTPS = False
    PUBLIC_DOMAIN_USES_HTTPS = True
#    USE_SUBDOMAIN = False
    USE_SUBDOMAIN = False
    PUBLIC_API_URL = 'https://{}'.format(PRODUCTION_DOMAIN)
    # Some endpoints from the API can be proxied on other domain
    # or use the same domain where the docs are being served
    # (omit the host if that's the case).
    RTD_PROXIED_API_URL = PUBLIC_API_URL
    RTD_EXTERNAL_VERSION_DOMAIN = 'external-builds.readthedocs.io'

    # Doc Builder Backends
    MKDOCS_BACKEND = 'readthedocs.doc_builder.backends.mkdocs'
    SPHINX_BACKEND = 'readthedocs.doc_builder.backends.sphinx'

    # slumber settings
    SLUMBER_API_HOST = 'https://readthedocs.org'
    SLUMBER_USERNAME = None
    SLUMBER_PASSWORD = None

    # Email
    DEFAULT_FROM_EMAIL = 'no-reply@readthedocs.org'
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
    SUPPORT_EMAIL = None

    # Sessions
    SESSION_COOKIE_DOMAIN = 'readthedocs.org'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 30 * 24 * 60 * 60  # 30 days
    SESSION_SAVE_EVERY_REQUEST = True
    # This cookie is used in cross-origin API requests from *.readthedocs.io to readthedocs.org
    SESSION_COOKIE_SAMESITE = None

    # CSRF
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_AGE = 30 * 24 * 60 * 60

    # Security & X-Frame-Options Middleware
    # https://docs.djangoproject.com/en/1.11/ref/middleware/#django.middleware.security.SecurityMiddleware
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # Content Security Policy
    # https://django-csp.readthedocs.io/
    CSP_BLOCK_ALL_MIXED_CONTENT = True
    CSP_DEFAULT_SRC = None  # This could be improved
    CSP_FRAME_ANCESTORS = ("'none'",)
    CSP_OBJECT_SRC = ("'none'",)
    CSP_REPORT_URI = None
    CSP_REPORT_ONLY = True  # Set to false to enable CSP in blocking mode
    CSP_EXCLUDE_URL_PREFIXES = (
        "/admin/",
    )

    # Read the Docs
    READ_THE_DOCS_EXTENSIONS = ext
    RTD_LATEST = 'latest'
    RTD_LATEST_VERBOSE_NAME = 'latest'
    RTD_STABLE = 'stable'
    RTD_STABLE_VERBOSE_NAME = 'stable'
    RTD_CLEAN_AFTER_BUILD = False

    # Database and API hitting settings
    DONT_HIT_API = False
    DONT_HIT_DB = True

    SYNC_USER = getpass.getuser()

    USER_MATURITY_DAYS = 7

    # override classes
    CLASS_OVERRIDES = {}

#    DOC_PATH_PREFIX = '_/'
    DOC_PATH_PREFIX = '_/'

    # Application classes
    @property
    def INSTALLED_APPS(self):  # noqa
        apps = [
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.staticfiles',
            'django.contrib.messages',
            'django.contrib.humanize',

            # third party apps
            'dj_pagination',
            'taggit',
            'django_gravatar',
            'rest_framework',
            'rest_framework.authtoken',
            'corsheaders',
            'textclassifier',
            'annoying',
            'django_extensions',
            'crispy_forms',
            'messages_extends',
            'django_elasticsearch_dsl',
            'django_filters',
            'polymorphic',

            # our apps
            'readthedocs.projects',
            'readthedocs.builds',
            'readthedocs.core',
            'readthedocs.doc_builder',
            'readthedocs.oauth',
            'readthedocs.redirects',
            'readthedocs.rtd_tests',
            'readthedocs.api.v2',
            'readthedocs.api.v3',

            'readthedocs.gold',
            'readthedocs.payments',
            'readthedocs.notifications',
            'readthedocs.integrations',
            'readthedocs.analytics',
            'readthedocs.sphinx_domains',
            'readthedocs.search',


            # allauth
            'allauth',
            'allauth.account',
            'allauth.socialaccount',
            'allauth.socialaccount.providers.github',
            'allauth.socialaccount.providers.gitlab',
            'allauth.socialaccount.providers.bitbucket',
            'allauth.socialaccount.providers.bitbucket_oauth2',
        ]
        if ext:
            apps.append('django_countries')
            apps.append('readthedocsext.donate')
            apps.append('readthedocsext.embed')
            apps.append('readthedocsext.spamfighting')
        return apps

    @property
    def USE_PROMOS(self):  # noqa
        return 'readthedocsext.donate' in self.INSTALLED_APPS

    MIDDLEWARE = (
        'readthedocs.core.middleware.ReadTheDocsSessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'dj_pagination.middleware.PaginationMiddleware',
        'readthedocs.core.middleware.SubdomainMiddleware',
        'readthedocs.core.middleware.SingleVersionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'csp.middleware.CSPMiddleware',
    )


#costa
# Baseline configuration.
#    AUTH_LDAP_SERVER_URI = "ldap://ds.infn.it"
    AUTH_LDAP_SERVER_URI = "ldaps://ds.infn.it"
    AUTH_LDAP_BIND_DN = "cn=daemon,dc=cnaf,dc=infn,dc=it"
    AUTH_LDAP_BIND_PASSWORD = "43fd3780-428c-4d93-87b1-c3c5ef63b60a"
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        "ou=People,dc=infn,dc=it", ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
    )


#    AUTH_LDAP_USER_DN_TEMPLATE =::: 'uid=%(user)s,ou=People,dc=infn,dc=it'
#    AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,ou=People,dc=infn,dc=it'
# Set up the basic group parameters.
#    AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
#        "ou=People,dc=infn,dc=it",
#        "ou=People,dc=infn,dc=it",
#        ldap.SCOPE_SUBTREE,
#        "(objectClass=groupOfNames)",
#    )
#    AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
# Simple group restrictions
#    AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=People,dc=infn,dc=it"
#    AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=Pedople,dc=infn,dc=it"
# Populate the Django user from the LDAP directory.
#    AUTH_LDAP_USER_ATTR_MAP = {
#        "first_name": "givenName",
#        "last_name": "sn",
#        "email": "mail",
#    }
#AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_active": "cn=active,ou=django,ou=groups,dc=example,dc=com",
#    "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
#    "is_superuser": "cn=superuser,ou=django,ou=groups,dc=example,dc=com",
#}
# This is the default, but I like to be explicit.
#    AUTH_LDAP_ALWAYS_UPDATE_USER = True
# Use LDAP group membership to calculate group permissions.
#    AUTH_LDAP_FIND_GROUP_PERMS = True
# Cache distinguished names and group memberships for an hour to minimize
# LDAP traffic.
#    AUTH_LDAP_CACHE_TIMEOUT = 3600
#costa







    AUTHENTICATION_BACKENDS = (
        # Needed to login by username in Django admin, regardless of `allauth`
        'django.contrib.auth.backends.ModelBackend',
        # `allauth` specific authentication methods, such as login by e-mail
        'allauth.account.auth_backends.AuthenticationBackend',
#costa
        'django_auth_ldap.backend.LDAPBackend'
#costa
    )

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 9,
            }
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    MESSAGE_STORAGE = 'readthedocs.notifications.storages.FallbackUniqueStorage'

    NOTIFICATION_BACKENDS = [
        'readthedocs.notifications.backends.EmailBackend',
        'readthedocs.notifications.backends.SiteBackend',
    ]

    # Paths
    SITE_ROOT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TEMPLATE_ROOT = os.path.join(SITE_ROOT, 'readthedocs', 'templates')
    DOCROOT = os.path.join(SITE_ROOT, 'user_builds')
    UPLOAD_ROOT = os.path.join(SITE_ROOT, 'user_uploads')
    CNAME_ROOT = os.path.join(SITE_ROOT, 'cnames')
    LOGS_ROOT = os.path.join(SITE_ROOT, 'logs')
    PRODUCTION_ROOT = os.path.join(SITE_ROOT, 'prod_artifacts')
    PRODUCTION_MEDIA_ARTIFACTS = os.path.join(PRODUCTION_ROOT, 'media')

    # Assets and media
    STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
    STATIC_URL = '/static/'
    MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')
    MEDIA_URL = '/media/'
    ADMIN_MEDIA_PREFIX = '/media/admin/'
    STATICFILES_DIRS = [
        os.path.join(SITE_ROOT, 'readthedocs', 'static'),
        os.path.join(SITE_ROOT, 'media'),
    ]
    STATICFILES_FINDERS = [
        'readthedocs.core.static.SelectiveFileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]
    PYTHON_MEDIA = False

    # Django Storage subclass used to write build artifacts to cloud or local storage
    # https://docs.readthedocs.io/page/development/settings.html#rtd-build-media-storage
    RTD_BUILD_MEDIA_STORAGE = 'readthedocs.builds.storage.BuildMediaFileSystemStorage'
    RTD_BUILD_ENVIRONMENT_STORAGE = 'readthedocs.builds.storage.BuildMediaFileSystemStorage'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [TEMPLATE_ROOT],
            'OPTIONS': {
                'debug': DEBUG,
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.request',
                    # Read the Docs processor
                    'readthedocs.core.context_processors.readthedocs_processor',
                ],
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ],
            },
        },
    ]

    # Cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'PREFIX': 'docs',
        }
    }
    CACHE_MIDDLEWARE_SECONDS = 60

    # I18n
    TIME_ZONE = 'UTC'
    USE_TZ = True
    LANGUAGE_CODE = 'en-us'
    LANGUAGES = (
        ('ca', gettext('Catalan')),
        ('en', gettext('English')),
        ('es', gettext('Spanish')),
        ('pt-br', gettext('Brazilian Portuguese')),
        ('nb', gettext('Norwegian Bokmål')),
        ('fr', gettext('French')),
        ('ru', gettext('Russian')),
        ('de', gettext('German')),
        ('gl', gettext('Galician')),
        ('vi', gettext('Vietnamese')),
        ('zh-cn', gettext('Simplified Chinese')),
        ('zh-tw', gettext('Traditional Chinese')),
        ('ja', gettext('Japanese')),
        ('uk', gettext('Ukrainian')),
        ('it', gettext('Italian')),
        ('ko', gettext('Korean')),
    )
    LOCALE_PATHS = [
        os.path.join(SITE_ROOT, 'readthedocs', 'locale'),
    ]
    USE_I18N = True
    USE_L10N = True

    # Celery
    CELERY_APP_NAME = 'readthedocs'
    CELERY_ALWAYS_EAGER = True
    CELERYD_TASK_TIME_LIMIT = 60 * 60  # 60 minutes
    CELERY_SEND_TASK_ERROR_EMAILS = False
    CELERYD_HIJACK_ROOT_LOGGER = False
    # This stops us from pre-fetching a task that then sits around on the builder
    CELERY_ACKS_LATE = True
    # Don't queue a bunch of tasks in the workers
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_CREATE_MISSING_QUEUES = True

    CELERY_DEFAULT_QUEUE = 'celery'
    CELERYBEAT_SCHEDULE = {
        # Ran every hour on minute 30
        'hourly-remove-orphan-symlinks': {
            'task': 'readthedocs.projects.tasks.broadcast_remove_orphan_symlinks',
            'schedule': crontab(minute=30),
            'options': {'queue': 'web'},
        },
        'quarter-finish-inactive-builds': {
            'task': 'readthedocs.projects.tasks.finish_inactive_builds',
            'schedule': crontab(minute='*/15'),
            'options': {'queue': 'web'},
        },
        'every-three-hour-clear-persistent-messages': {
            'task': 'readthedocs.core.tasks.clear_persistent_messages',
            'schedule': crontab(minute=0, hour='*/3'),
            'options': {'queue': 'web'},
        },
        'every-day-delete-old-search-queries': {
            'task': 'readthedocs.search.tasks.delete_old_search_queries_from_db',
            'schedule': crontab(minute=0, hour=0),
            'options': {'queue': 'web'},
        }
    }
    MULTIPLE_APP_SERVERS = [CELERY_DEFAULT_QUEUE]
    MULTIPLE_BUILD_SERVERS = [CELERY_DEFAULT_QUEUE]

    # Sentry
    SENTRY_CELERY_IGNORE_EXPECTED = True

    # Docker
    DOCKER_ENABLE = False
    DOCKER_SOCKET = 'unix:///var/run/docker.sock'
    # This settings has been deprecated in favor of DOCKER_IMAGE_SETTINGS
    DOCKER_BUILD_IMAGES = None
    DOCKER_LIMITS = {'memory': '200m', 'time': 600}

    # User used to create the container.
    # In production we use the same user than the one defined by the
    # ``USER docs`` instruction inside the Dockerfile.
    # In development, we can use the "UID:GID" of the current user running the
    # instance to avoid file permissions issues.
    # https://docs.docker.com/engine/reference/run/#user
    RTD_DOCKER_USER = 'docs:docs'

    RTD_DOCKER_COMPOSE = False

    DOCKER_DEFAULT_IMAGE = 'readthedocs/build'
    DOCKER_VERSION = 'auto'
    DOCKER_DEFAULT_VERSION = 'latest'
    DOCKER_IMAGE = '{}:{}'.format(DOCKER_DEFAULT_IMAGE, DOCKER_DEFAULT_VERSION)
    DOCKER_IMAGE_SETTINGS = {
        # A large number of users still have this pinned in their config file.
        # We must have documented it at some point.
        'readthedocs/build:2.0': {
            'python': {
                'supported_versions': [2, 2.7, 3, 3.5],
                'default_version': {
                    2: 2.7,
                    3: 3.5,
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

    # Alias tagged via ``docker tag`` on the build servers
    DOCKER_IMAGE_SETTINGS.update({
        'readthedocs/build:stable': DOCKER_IMAGE_SETTINGS.get('readthedocs/build:5.0'),
        'readthedocs/build:latest': DOCKER_IMAGE_SETTINGS.get('readthedocs/build:6.0'),
        'readthedocs/build:testing': DOCKER_IMAGE_SETTINGS.get('readthedocs/build:7.0'),
    })

    # All auth
    ACCOUNT_ADAPTER = 'readthedocs.core.adapters.AccountAdapter'
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
    ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
    ACCOUNT_ACTIVATION_DAYS = 7
    SOCIALACCOUNT_AUTO_SIGNUP = False
    SOCIALACCOUNT_PROVIDERS = {
        'github': {
            'SCOPE': [
                'user:email',
                'read:org',
                'admin:repo_hook',
                'repo:status',
            ],
        },
        'gitlab': {
            'SCOPE': [
                'api',
                'read_user',
            ],
        },
    }

    # CORS
    CORS_ORIGIN_REGEX_WHITELIST = (
        r'^http://(.+)\.readthedocs\.io$',
        r'^https://(.+)\.readthedocs\.io$',
    )
    # So people can post to their accounts
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'x-csrftoken'
    )

    # RTD Settings
    REPO_LOCK_SECONDS = 30
    ALLOW_PRIVATE_REPOS = False
    DEFAULT_PRIVACY_LEVEL = 'public'
    DEFAULT_VERSION_PRIVACY_LEVEL = 'public'
    GROK_API_HOST = 'https://api.grokthedocs.com'
    SERVE_DOCS = ['public']
    ALLOW_ADMIN = True

    # Elasticsearch settings.
    ES_HOSTS = ['search:9200']
    ELASTICSEARCH_DSL = {
        'default': {
            'hosts': 'search:9200'
        },
    }
    # Chunk size for elasticsearch reindex celery tasks
    ES_TASK_CHUNK_SIZE = 100

    # Info from Honza about this:
    # The key to determine shard number is actually usually not the node count,
    # but the size of your data.
    # There are advantages to just having a single shard in an index since
    # you don't have to do the distribute/collect steps when executing a search.
    # If your data will allow it (not significantly larger than 40GB)
    # I would recommend going to a single shard and one replica meaning
    # any of the two nodes will be able to serve any search without talking to the other one.
    # Scaling to more searches will then just mean adding a third node
    # and a second replica resulting in immediate 50% bump in max search throughput.

    ES_INDEXES = {
        'project': {
            'name': 'project_index',
            'settings': {'number_of_shards': 1,
                         'number_of_replicas': 1
                         }
        },
        'page': {
            'name': 'page_index',
            'settings': {
                'number_of_shards': 1,
                'number_of_replicas': 1,
            }
        },
    }

    # ANALYZER = 'analysis': {
    #     'analyzer': {
    #         'default_icu': {
    #             'type': 'custom',
    #             'tokenizer': 'icu_tokenizer',
    #             'filter': ['word_delimiter', 'icu_folding', 'icu_normalizer'],
    #         }
    #     }
    # }

    # Disable auto refresh for increasing index performance
    ELASTICSEARCH_DSL_AUTO_REFRESH = False

    ALLOWED_HOSTS = ['*']

    ABSOLUTE_URL_OVERRIDES = {
        'auth.user': lambda o: '/profiles/{}/'.format(o.username)
    }

    INTERNAL_IPS = ('127.0.0.1',)

    # Taggit
    # https://django-taggit.readthedocs.io
    TAGGIT_TAGS_FROM_STRING = 'readthedocs.projects.tag_utils.rtd_parse_tags'

    # Stripe
    STRIPE_SECRET = None
    STRIPE_PUBLISHABLE = None

    # Do Not Track support
    DO_NOT_TRACK_ENABLED = False

    # Misc application settings
    GLOBAL_ANALYTICS_CODE = None
    DASHBOARD_ANALYTICS_CODE = None  # For the dashboard, not docs
    GRAVATAR_DEFAULT_IMAGE = 'https://assets.readthedocs.org/static/images/silhouette.png'  # NOQA
    OAUTH_AVATAR_USER_DEFAULT_URL = GRAVATAR_DEFAULT_IMAGE
    OAUTH_AVATAR_ORG_DEFAULT_URL = GRAVATAR_DEFAULT_IMAGE
    RESTRICTEDSESSIONS_AUTHED_ONLY = True
    RESTRUCTUREDTEXT_FILTER_SETTINGS = {
        'cloak_email_addresses': True,
        'file_insertion_enabled': False,
        'raw_enabled': False,
        'strip_comments': True,
        'doctitle_xform': True,
        'sectsubtitle_xform': True,
        'initial_header_level': 2,
        'report_level': 5,
        'syntax_highlight': 'none',
        'math_output': 'latex',
        'field_name_limit': 50,
    }
    REST_FRAMEWORK = {
        'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',  # NOQA
        'DEFAULT_THROTTLE_RATES': {
            'anon': '5/minute',
            'user': '60/minute',
        },
        'PAGE_SIZE': 10,
        'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    }

    SILENCED_SYSTEM_CHECKS = ['fields.W342']

    # Logging
    LOG_FORMAT = '%(name)s:%(lineno)s[%(process)d]: %(levelname)s %(message)s'
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'default': {
                'format': LOG_FORMAT,
                'datefmt': '%d/%b/%Y %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'debug': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOGS_ROOT, 'debug.log'),
                'formatter': 'default',
            },
            'null': {
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['debug', 'console'],
                # Always send from the root, handlers can filter levels
                'level': 'DEBUG',
            },
            'readthedocs': {
                'handlers': ['debug', 'console'],
                'level': 'DEBUG',
                # Don't double log at the root logger for these.
                'propagate': False,
            },
            'django.security.DisallowedHost': {
                'handlers': ['null'],
                'propagate': False,
            },
        },
    }
