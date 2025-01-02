from django.urls import path
from .import views

urlpatterns=[
    path("", views.landing, name="landing"),
    path("parent/signup/", views.parent_signup, name="parent_signup"),
    path("parent/login/", views.parent_login, name="parent_login"),
    path("child/signup/<int:parent_id>/", views.child_signup, name="child_signup"),
    path("child/login/", views.child_login, name="child_login"),
    path("costs/<int:child_id>/", views.costs, name="costs"),
    path("child/dashboard/<int:child_id>/", views.child_dashboard, name="child_dashboard"),
    path("parent/dashboard/<int:child_id>/", views.parent_dashboard, name="parent_dashboard"),
    path("goals/<int:child_id>/", views.goals, name="goals" ),
    path("details/<int:child_id>/", views.details, name="details"),
    path('education/<int:child_id>/', views.education, name='education'),

]



