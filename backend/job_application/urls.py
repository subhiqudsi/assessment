from django.urls import path
from .views import (
    CandidateRegistrationView,
    CandidateStatusView,
    CandidateStatusHistoryView,
    AdminCandidateListView,
    AdminCandidateDetailView,
    AdminStatusUpdateView,
    AdminResumeDownloadView,
)

app_name = 'job_application'

urlpatterns = [
    # Candidate endpoints
    path('candidates/', CandidateRegistrationView.as_view(), name='candidates'),  # POST for registration
    path('candidates/status/', CandidateStatusView.as_view(), name='candidate_status'),  # GET with email param
    path('candidates/<int:candidate_id>/history/', CandidateStatusHistoryView.as_view(), name='candidate_history'),
    
    # Admin endpoints
    path('admin/candidates/', AdminCandidateListView.as_view(), name='admin_candidates'),  # GET list
    path('admin/candidates/<int:candidate_id>/', AdminCandidateDetailView.as_view(), name='admin_candidate_detail'),  # GET detail
    path('admin/candidates/<int:candidate_id>/status/', AdminStatusUpdateView.as_view(), name='admin_candidate_status'),  # PATCH status
    path('admin/candidates/<int:candidate_id>/resume/', AdminResumeDownloadView.as_view(), name='admin_candidate_resume'),  # GET download
]
