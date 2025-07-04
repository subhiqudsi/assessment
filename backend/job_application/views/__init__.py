from .candidate_registration import CandidateRegistrationView
from .candidate_status import CandidateStatusView
from .candidate_status_history import CandidateStatusHistoryView
from .admin_candidate_list import AdminCandidateListView, CandidatePagination
from .admin_candidate_detail import AdminCandidateDetailView
from .admin_status_update import AdminStatusUpdateView
from .admin_resume_download import AdminResumeDownloadView

__all__ = [
    'CandidateRegistrationView',
    'CandidateStatusView',
    'CandidateStatusHistoryView',
    'AdminCandidateListView',
    'AdminCandidateDetailView',
    'AdminStatusUpdateView',
    'AdminResumeDownloadView',
    'CandidatePagination',
]