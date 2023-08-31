from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from myapp.views import RemoteSensingDataView, PublishDataView, UserCreate, UserLogin, \
    check_username, custom_captcha_refresh, check_login_status, change_password, logout, get_data_directory, get_browse_image
from captcha.views import captcha_image

router = DefaultRouter()
router.register(r'data', RemoteSensingDataView)

urlpatterns = [
    path('api/', include(router.urls)),
    # path('api/scan-data/', ScanDataView.as_view()),
    path('api/publish-data/', PublishDataView.as_view()),
    path('api/v1/users/', UserCreate.as_view(), name='user-create'),
    path('api/v1/login/', UserLogin.as_view(), name='user-login'),
    path('api/v1/check_username/', check_username, name='check_username'),
    path('custom_captcha/refresh/', custom_captcha_refresh, name='custom_captcha_refresh'),
    path('captcha/', include('captcha.urls')),
    path('api/v1/check_login_status/', check_login_status, name='check_login_status'),
    path('api/v1/change_password/', change_password, name='change_password'),
    path('api/v1/logout/', logout, name='logout'),
    path('api/v1/data_directory/', get_data_directory, name='data_directory'),
    path('get_image/<int:data_id>/', get_browse_image, name='get_browse_image'),
]

