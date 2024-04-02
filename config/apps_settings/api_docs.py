SPECTACULAR_SETTINGS = {
    'TITLE': 'GHOFLE API',
    'DESCRIPTION': 'Ghofle is a web service for securely exchanging your files. With Ghofle, you can easily sell'
                   ' your files. For enhanced file security, the AMAZON AWS S3 storage service is utilized, and'
                   ' expiring links are issued.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    # OTHER SETTINGS
    'PLUGINS': [
        'drf_spectacular.plugins.AuthPlugin',
    ],
    # 'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAdminUser'],
    # Auth with session only in docs without effect to api
    'SERVE_AUTHENTICATION': ["rest_framework.authentication.SessionAuthentication",
                             "rest_framework_simplejwt.authentication.JWTAuthentication"],
}
