from django.urls import path

from . import views

app_name = "design_studio"

urlpatterns = [
    path("", views.studio_view, name="studio"),
    path("save/", views.save_studio_view, name="save"),
    path("toggle-night/", views.toggle_night_mode_view, name="toggle_night"),
    path("toggle-menu-layout/", views.toggle_menu_layout_view, name="toggle_menu_layout"),
    path("export/", views.export_theme_json_view, name="export"),
    path("import/", views.import_theme_json_view, name="import"),
]
