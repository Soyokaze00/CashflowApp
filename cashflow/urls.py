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
    # path('delete-cost/<int:cost_id>/', views.delete_cost, name='delete_cost'),
    # path("costsV2/<int:child_id>/", views.costs, name="costsV2")
    
    # path("parent/dashboard/", views.parent_dashboard, name="parent_dashboard"),
]



