"""
Instance app model mixins - OpenEdX Instance Configuration
"""

# Imports #####################################################################

from django.db import models
from django.conf import settings


# Classes #####################################################################

class OpenEdXConfigMixin(models.Model):
    """
    Stores the instance configuration template for ansible variables
    """
    class Meta:
        abstract = True

    def _get_configuration_variables(self):
        """
        Creates and returns a dictionary of ansible configuration variables for the instance
        """
        template = {
            # System
            "COMMON_HOSTNAME": self.instance.domain,
            "COMMON_ENVIRONMENT": "opencraft",
            "COMMON_DEPLOYMENT": self.instance.internal_lms_domain,
            # Set the default fallback DNS servers to be Google's DNS. This is necessary to eliminate a single
            # point of failure with OVH DNS (which we've seen slow down and become unavailable from time to time).
            "COMMON_FALLBACK_DNS_SERVERS": [
                "8.8.8.8",
                "8.8.4.4"
            ],

            # HTTP authentication
            "COMMON_ENABLE_BASIC_AUTH": True,
            "COMMON_HTPASSWD_USER": self.instance.http_auth_user,
            "COMMON_HTPASSWD_PASS": self.instance.http_auth_pass,

            # OAuth2 / JWT issuer settings
            "COMMON_OAUTH_BASE_URL": "{{ EDXAPP_LMS_ROOT_URL }}",
            "COMMON_JWT_SECRET_KEY": "{{ EDXAPP_JWT_SECRET_KEY }}",
            "COMMON_JWT_AUDIENCE": 'lms-key',

            # edxapp
            "EDXAPP_PLATFORM_NAME": self.instance.name,
            "EDXAPP_SITE_NAME": self.instance.domain,
            "EDXAPP_LMS_NGINX_PORT": 80,
            "EDXAPP_LMS_SSL_NGINX_PORT": 443,
            "EDXAPP_LMS_BASE_SCHEME": 'https',
            "EDXAPP_LMS_SITE_NAME": self.instance.domain,
            "EDXAPP_LMS_BASE": self.instance.domain,

            "EDXAPP_LMS_PREVIEW_NGINX_PORT": 80,
            "EDXAPP_PREVIEW_LMS_BASE": self.instance.lms_preview_domain,

            "EDXAPP_CMS_NGINX_PORT": 80,
            "EDXAPP_CMS_SSL_NGINX_PORT": 443,
            "EDXAPP_CMS_SITE_NAME": self.instance.studio_domain,
            "EDXAPP_CMS_BASE": self.instance.studio_domain,
            "CMS_HOSTNAME": '~{}'.format(self.instance.studio_domain_nginx_regex),

            # Set this to a string such as ".myinstance.org" to enable session sharing between LMS and the Studio.
            # We cannot do this on OC IM for security reasons (we don't want different *instances* to share cookies).
            "EDXAPP_SESSION_COOKIE_DOMAIN": '',

            # Nginx
            "NGINX_SET_X_FORWARDED_HEADERS": False,

            # SSL is handled on the load balancer, and the appservers are HTTP only.
            "NGINX_ENABLE_SSL": False,
            "NGINX_REDIRECT_TO_HTTPS": False,

            # Nginx redirects (optional)
            # This example redirects non-www to www version of myinstance.org.
            # nginx_redirects:
            #   no_www_to_www:
            #     server_names: ['myinstance.org']
            #     redirect_destination: 'https://www.myinstance.org'
            #     ssl: true

            # Forum environment settings
            "FORUM_RACK_ENV": 'production',
            "FORUM_SINATRA_ENV": 'production',

            # Emails
            "EDXAPP_CONTACT_EMAIL": self.email,
            "EDXAPP_TECH_SUPPORT_EMAIL": self.email,
            "EDXAPP_BUGS_EMAIL": self.email,
            "EDXAPP_FEEDBACK_SUBMISSION_EMAIL": self.email,
            "EDXAPP_DEFAULT_FROM_EMAIL": self.email,
            "EDXAPP_DEFAULT_FEEDBACK_EMAIL": self.email,
            "EDXAPP_SERVER_EMAIL": self.email,
            "EDXAPP_BULK_EMAIL_DEFAULT_FROM_EMAIL": self.email,
            "ECOMMERCE_OSCAR_FROM_EMAIL": self.email,

            "EDXAPP_EMAIL_BACKEND": 'django.core.mail.backends.smtp.EmailBackend',
            "EDXAPP_EMAIL_HOST": 'localhost',
            "EDXAPP_EMAIL_PORT": 25,
            "EDXAPP_EMAIL_HOST_USER": '',
            "EDXAPP_EMAIL_HOST_PASSWORD": '',
            "EDXAPP_EMAIL_USE_TLS": False,

            # Security updates
            "COMMON_SECURITY_UPDATES": True,
            "SECURITY_UNATTENDED_UPGRADES": True,
            "SECURITY_UPDATE_ALL_PACKAGES": False,
            "SECURITY_UPGRADE_ON_ANSIBLE": True,

            # OAuth
            "EDXAPP_OAUTH_ENFORCE_SECURE": False,

            # Set YouTube API key to null to avoid YouTube XHR errors.
            # Can be overridden in extra settings with a valid API key.
            "EDXAPP_YOUTUBE_API_KEY": None,

            # Set analytics url to an empty string to hide links to Insights on instructor dashboard.
            # For installations that include analytics, this should be set to the base Insights URL.
            "EDXAPP_ANALYTICS_DASHBOARD_URL": '',

            # Notifier (forum digest notifications)
            "NOTIFIER_DIGEST_TASK_INTERVAL": '1440',  # 1440 minutes == 24 hours
            "NOTIFIER_DIGEST_EMAIL_SENDER": self.email,
            "NOTIFIER_LMS_URL_BASE": 'https://{}'.format(self.instance.domain),
            "NOTIFIER_LOGO_IMAGE_URL": 'https://{}/static/images/logo.png'.format(self.instance.domain),

            "NOTIFIER_EMAIL_BACKEND": 'smtp',
            "NOTIFIER_EMAIL_HOST": 'localhost',
            "NOTIFIER_EMAIL_PORT": 25,
            "NOTIFIER_EMAIL_USER": '',
            "NOTIFIER_EMAIL_PASS": '',
            "NOTIFIER_EMAIL_USE_TLS": False,

            # Repositories URLs
            "edx_ansible_source_repo": self.configuration_source_repo_url,
            "edx_platform_repo": self.edx_platform_repository_url,

            # Pin down dependencies to specific (known to be compatible) commits.
            "edx_platform_version": self.edx_platform_commit,
            "configuration_version": self.configuration_version,
            "forum_version": self.openedx_release,
            "xqueue_version": self.openedx_release,
            "certs_version": self.openedx_release,
            "NOTIFIER_VERSION": self.openedx_release,
            "ANALYTICS_API_VERSION": self.openedx_release,
            "INSIGHTS_VERSION": self.openedx_release,
            "ECOMMERCE_VERSION": self.openedx_release,

            # Misc
            "EDXAPP_LANG": 'en_US.UTF-8',
            "EDXAPP_TIME_ZONE": 'UTC',

            # Available as ENV_TOKENS in the django setting files.
            "EDXAPP_ENV_EXTRA": {
                "LANGUAGE_CODE": 'en'
            },

            # Features
            "EDXAPP_FEATURES": {
                "ALLOW_ALL_ADVANCED_COMPONENTS": True,
                "AUTH_USE_OPENID": False,
                "CERTIFICATES_ENABLED": True,
                "CERTIFICATES_HTML_VIEW": True,
                "CUSTOM_CERTIFICATE_TEMPLATES_ENABLED": True,
                "ENABLE_COMBINED_LOGIN_REGISTRATION": True,
                "ENABLE_DISCUSSION_SERVICE": True,
                "ENABLE_DISCUSSION_HOME_PANEL": True,
                "ENABLE_DISCUSSION_EMAIL_DIGEST": True,
                "ENABLE_DJANGO_ADMIN_SITE": True,
                "ENABLE_INSTRUCTOR_ANALYTICS": True,
                "ENABLE_INSTRUCTOR_EMAIL": True,
                "ENABLE_OAUTH2_PROVIDER": True,
                "ENABLE_PEARSON_HACK_TEST": False,
                "ENABLE_GRADE_DOWNLOADS": True,
                "ENABLE_THIRD_PARTY_AUTH": True,
                "ENABLE_XBLOCK_VIEW_ENDPOINT": True,
                "ENABLE_SYSADMIN_DASHBOARD": True,
                "PREVIEW_LMS_BASE": self.instance.lms_preview_domain,
                "REQUIRE_COURSE_EMAIL_AUTH": False,
                "USE_MICROSITES": False,
                "PREVENT_CONCURRENT_LOGINS": False,
                # These are not part of the standard install:
                # "CUSTOM_COURSES_EDX": True,
                # "ENABLE_LTI_PROVIDER": True,
                # "ENABLE_PREREQUISITE_COURSES": True,
                # "ENABLE_PROCTORED_EXAMS": True,
                # "INDIVIDUAL_DUE_DATES": True,
                # "MILESTONES_APP": True,
            },

            # Gunicorn workers
            "EDXAPP_WORKERS": {
                "lms": 3,
                "cms": 2,
            },

            # Celery workers
            "EDXAPP_WORKER_DEFAULT_STOPWAITSECS": 1200,

            # Monitoring
            "COMMON_ENABLE_NEWRELIC": True if settings.NEWRELIC_LICENSE_KEY else False,
            "COMMON_ENABLE_NEWRELIC_APP": True if settings.NEWRELIC_LICENSE_KEY else False,
            "NEWRELIC_LICENSE_KEY": settings.NEWRELIC_LICENSE_KEY if settings.NEWRELIC_LICENSE_KEY else "",

            # Discovery
            "SANDBOX_ENABLE_DISCOVERY": False, # set to true to enable discovery
            "DISCOVERY_ELASTICSEARCH_URL": 'http://localhost:9200',
            "DISCOVERY_URL_ROOT": 'https://{}'.format(self.instance.discovery_domain),
            "DISCOVERY_HOSTNAME": '~{}'.format(self.instance.discovery_domain_nginx_regex),
            "DISCOVERY_NGINX_PORT": 80,
            "DISCOVERY_SSL_NGINX_PORT": 443,

            # Ecommerce
            "SANDBOX_ENABLE_ECOMMERCE": False,  # set to true to enable ecommerce
            "ECOMMERCE_NGINX_PORT": 80,
            "ECOMMERCE_SSL_NGINX_PORT": 443,
            "ECOMMERCE_HOSTNAME": '~{}'.format(self.instance.ecommerce_domain_nginx_regex),
            "ECOMMERCE_ECOMMERCE_URL_ROOT": 'https://{}'.format(self.instance.ecommerce_domain),
            "EDXAPP_ECOMMERCE_PUBLIC_URL_ROOT": 'https://{}'.format(self.instance.ecommerce_domain),
            "EDXAPP_ECOMMERCE_API_URL": 'https://{}/api/v2'.format(self.instance.ecommerce_domain),
            "ECOMMERCE_SUPPORT_URL": 'https://{}'.format(self.instance.domain),
            "ECOMMERCE_LMS_URL_ROOT": 'https://{}'.format(self.instance.domain),
            "ECOMMERCE_COURSE_CATALOG_URL": 'https://{}'.format(self.instance.discovery_domain),

            "ECOMMERCE_PLATFORM_NAME": '"{{ EDXAPP_PLATFORM_NAME }}"',
            # Set your own ECOMMERCE_PAYMENT_PROCESSOR_CONFIG, or update the variables for the appropriate processor:
            # * CyberSource
            "ECOMMERCE_CYBERSOURCE_PROFILE_ID": 'SET-ME-PLEASE',
            "ECOMMERCE_CYBERSOURCE_MERCHANT_ID": 'SET-ME-PLEASE',
            "ECOMMERCE_CYBERSOURCE_ACCESS_KEY": 'SET-ME-PLEASE',
            "ECOMMERCE_CYBERSOURCE_SECRET_KEY": 'SET-ME-PLEASE',
            "ECOMMERCE_CYBERSOURCE_TRANSACTION_KEY": 'SET-ME-PLEASE',
            "ECOMMERCE_CYBERSOURCE_PAYMENT_PAGE_URL": 'https://set-me-please',
            "ECOMMERCE_CYBERSOURCE_RECEIPT_PAGE_URL": '{{ ECOMMERCE_LMS_URL_ROOT }}/commerce/checkout/receipt/',
            "ECOMMERCE_CYBERSOURCE_CANCEL_PAGE_URL": '{{ ECOMMERCE_LMS_URL_ROOT }}/commerce/checkout/cancel/',
            "ECOMMERCE_CYBERSOURCE_SOAP_API_URL": 'https://set-me-please',
            # * PayPal
            "ECOMMERCE_PAYPAL_MODE": 'SET-ME-PLEASE',
            "ECOMMERCE_PAYPAL_CLIENT_ID": 'SET-ME-PLEASE',
            "ECOMMERCE_PAYPAL_CLIENT_SECRET": 'SET-ME-PLEASE',
            "ECOMMERCE_PAYPAL_RECEIPT_URL": '{{ ECOMMERCE_LMS_URL_ROOT }}/commerce/checkout/receipt/',
            "ECOMMERCE_PAYPAL_CANCEL_URL": '{{ ECOMMERCE_LMS_URL_ROOT }}/commerce/checkout/cancel/',
            "ECOMMERCE_PAYPAL_ERROR_URL": '{{ ECOMMERCE_LMS_URL_ROOT }}/commerce/checkout/error/',
        }

        if self.smtp_relay_settings:
            template.update({
                "POSTFIX_QUEUE_EXTERNAL_SMTP_HOST": self.smtp_relay_settings["host"],
                "POSTFIX_QUEUE_EXTERNAL_SMTP_PORT": str(self.smtp_relay_settings["port"]),
                "POSTFIX_QUEUE_EXTERNAL_SMTP_USER": self.smtp_relay_settings["username"],
                "POSTFIX_QUEUE_EXTERNAL_SMTP_PASSWORD": self.smtp_relay_settings["password"],
                # The following two settings ensure that original From address is copied into the Reply-To header,
                # after which the original From address is replaced with an address constructed from instance domain
                # and the INSTANCE_SMTP_RELAY_SENDER_DOMAIN setting, for example: lms.myinstance.org@opencraft.hosting.
                "POSTFIX_QUEUE_HEADER_CHECKS": '/^From:(.*)$/   PREPEND Reply-To:$1',
                "POSTFIX_QUEUE_SENDER_CANONICAL_MAPS": '{}  {}'.format(
                    self.smtp_relay_settings["source_address"],
                    self.smtp_relay_settings["rewritten_address"]
                ),
            })

        if self.github_admin_username_list:
            template.update({
                "COMMON_USER_INFO": [
                    {
                        "name": github_username,
                        "github": True,
                        "type": "admin"
                    }
                    for github_username in self.github_admin_username_list
                ],
            })

        return template