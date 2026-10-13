
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # HR Authentication
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="recruitment/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    
    path(
      "candidates/<int:candidate_id>/resume/",
       views.candidate_resume,
    name="candidate_resume",
    ),


    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Candidates
    path("candidates/upload/", views.upload_resume, name="upload_resume"),
    path("candidates/compare/", views.compare_candidates, name="compare_candidates"),
    path("candidates/", views.candidate_list, name="candidate_list"),

    # Jobs
    path("jobs/", views.manage_jobs, name="manage_jobs"),
    path("jobs/<int:job_id>/edit/", views.edit_job, name="edit_job"),
    path("jobs/<int:job_id>/delete/", views.delete_job, name="delete_job"),

    # Admin Dashboard
    path("recruitment-admin/", views.admin_dashboard, name="admin_dashboard"),
]
