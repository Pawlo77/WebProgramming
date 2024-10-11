"""
URL configuration for book_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.static import serve
from utils.views import ContactUsView, about_view, home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("about/", about_view, name="about"),
    path("contact/", ContactUsView.as_view(), name="contact"),
    path("users/", include("users.urls")),
    path("items/", include("items.urls")),
    path("reviews/", include("reviews.urls")),
    path("people/", include("people.urls")),
    #
    # system
    path(
        "admin/password_change/",
        lambda request: redirect("/users/password_change/", permanent=True),
    ),
    path("admin/", admin.site.urls),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    #
    # 3rd party
    # re_path(r"^i18n/", include("django.conf.urls.i18n")),
]
