from django.urls import path
from . import views

app_name = 'job_application'

urlpatterns = [
    # Candidate Registration
    path('api/candidates/register/', views.CandidateRegistrationView.as_view(), name='candidate_register'),
    
    # Candidate Status Tracking
    path('api/candidates/<int:candidate_id>/status/', views.CandidateStatusView.as_view(), name='candidate_status'),
    path('api/candidates/status/', views.CandidateStatusView.as_view(), name='candidate_status_by_email'),
    path('api/candidates/<int:candidate_id>/history/', views.CandidateStatusHistoryView.as_view(), name='candidate_status_history'),
    
    # Admin Endpoints
    path('api/admin/candidates/', views.AdminCandidateListView.as_view(), name='admin_candidates_list'),
    path('api/admin/candidates/<int:candidate_id>/', views.AdminCandidateDetailView.as_view(), name='admin_candidate_detail'),
    path('api/admin/candidates/<int:candidate_id>/status/', views.AdminStatusUpdateView.as_view(), name='admin_status_update'),
    path('api/admin/candidates/<int:candidate_id>/download/', views.AdminResumeDownloadView.as_view(), name='admin_resume_download'),
]