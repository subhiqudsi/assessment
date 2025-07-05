'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { adminApi } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { DEPARTMENTS, STATUS_COLORS } from '@/utils/constants';
import { format } from 'date-fns';
import { Download, ChevronLeft, ChevronRight, History } from 'lucide-react';

interface Candidate {
  id: number;
  full_name: string;
  date_of_birth: string;
  years_of_experience: number;
  department: string;
  status: string;
  created_at: string;
}

interface PaginatedResponse {
  success: boolean;
  total_count: number;
  results: Candidate[];
  count: number;
  next: string | null;
  previous: string | null;
}

interface StatusHistoryItem {
  id: number;
  previous_status: string | null;
  previous_status_display: string | null;
  new_status: string;
  new_status_display: string;
  comments: string;
  changed_by: string;
  changed_at: string;
}

interface CandidateDetailResponse {
  success: boolean;
  candidate: {
    id: number;
    full_name: string;
    email: string;
    phone_number: string;
    date_of_birth: string;
    age: number;
    years_of_experience: number;
    department: string;
    department_display: string;
    status: string;
    status_display: string;
    has_resume: boolean;
    resume_filename: string;
    created_at: string;
    updated_at: string;
    status_history: StatusHistoryItem[];
  };
}

export default function AdminDashboard() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [department, setDepartment] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [feedback, setFeedback] = useState('');
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [candidateDetail, setCandidateDetail] = useState<CandidateDetailResponse | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {

    fetchCandidates();
  }, [ department, page]);

  const fetchCandidates = async () => {
    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        ...(department && { department }),
      });

      const response = await adminApi.get<PaginatedResponse>(`/candidates/?${params}`);
      setCandidates(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10)); // Assuming 10 items per page
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  };

  const downloadResume = async (candidateId: number, candidateName: string) => {
    try {
      const response = await adminApi.get(`/candidates/${candidateId}/resume/`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${candidateName}_resume.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      alert('Failed to download resume');
    }
  };

  const updateStatus = async () => {
    if (!selectedCandidate || !newStatus) return;

    try {
      await adminApi.patch(`/candidates/${selectedCandidate.id}/status/`, {
        status: newStatus,
        comments: feedback,
      });

      setShowStatusModal(false);
      setSelectedCandidate(null);
      setNewStatus('');
      setFeedback('');
      fetchCandidates();
    } catch (err: any) {
      alert('Failed to update status');
    }
  };

  const fetchCandidateDetail = async (candidateId: number) => {
    setHistoryLoading(true);
    try {
      const response = await adminApi.get<CandidateDetailResponse>(`/candidates/${candidateId}/`);
      setCandidateDetail(response.data);
      setShowHistoryModal(true);
    } catch (err: any) {
      alert('Failed to fetch candidate details');
    } finally {
      setHistoryLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    return STATUS_COLORS[status as keyof typeof STATUS_COLORS] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
            <Button onClick={() => router.push('/admin/login')} variant="secondary">
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex gap-4">
          <Select
            label="Filter by Department"
            options={[{ value: '', label: 'All Departments' }, ...DEPARTMENTS]}
            value={department}
            onChange={(e) => {
              setDepartment(e.target.value);
              setPage(1);
            }}
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <>
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">
                      Date of Birth
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">
                      Experience
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">
                      Department
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">
                      Applied On
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {candidates?.map((candidate) => (
                    <tr key={candidate.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-900">{candidate.full_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                        {format(new Date(candidate.date_of_birth), 'MMM dd, yyyy')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-900">{candidate.years_of_experience} years</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-900">{candidate.department}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(candidate.status)}`}>
                          {candidate.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                        {format(new Date(candidate.created_at), 'MMM dd, yyyy HH:mm')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => downloadResume(candidate.id, candidate.full_name)}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => fetchCandidateDetail(candidate.id)}
                            disabled={historyLoading}
                          >
                            <History className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => {
                              setSelectedCandidate(candidate);
                              setNewStatus(candidate.status);
                              setShowStatusModal(true);
                            }}
                          >
                            Update Status
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-6 flex justify-between items-center">
              <Button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                variant="secondary"
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Previous
              </Button>
              <span className="text-gray-900">
                Page {page} of {totalPages}
              </span>
              <Button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                variant="secondary"
              >
                Next
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </>
        )}
      </div>

      {showStatusModal && selectedCandidate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold mb-4 text-gray-900">Update Application Status</h2>
            <p className="text-gray-900 mb-4">
              Updating status for: <strong>{selectedCandidate.full_name}</strong>
            </p>

            <Select
              label="New Status"
              options={[
                { value: 'SUBMITTED', label: 'Submitted' },
                { value: 'UNDER_REVIEW', label: 'Under Review' },
                { value: 'INTERVIEW_SCHEDULED', label: 'Interview Scheduled' },
                { value: 'REJECTED', label: 'Rejected' },
                { value: 'ACCEPTED', label: 'Accepted' },
              ]}
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
            />

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-900 mb-1">
                Feedback (Optional)
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                rows={3}
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Enter feedback for the candidate..."
              />
            </div>

            <div className="flex gap-3">
              <Button onClick={updateStatus} className="flex-1">
                Update Status
              </Button>
              <Button
                onClick={() => {
                  setShowStatusModal(false);
                  setSelectedCandidate(null);
                  setNewStatus('');
                  setFeedback('');
                }}
                variant="secondary"
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {showHistoryModal && candidateDetail && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Candidate Details & Status History</h2>
                  <p className="text-gray-900 mt-1">
                    {candidateDetail.candidate.full_name} (ID: {candidateDetail.candidate.id})
                  </p>
                  <div className="flex items-center gap-4 mt-2">
                    <p className="text-sm text-gray-900">
                      Current Status: <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(candidateDetail.candidate.status_display)}`}>
                        {candidateDetail.candidate.status_display}
                      </span>
                    </p>
                    <p className="text-sm text-gray-900">
                      Department: {candidateDetail.candidate.department_display}
                    </p>
                    <p className="text-sm text-gray-900">
                      Experience: {candidateDetail.candidate.years_of_experience} years
                    </p>
                  </div>
                </div>
                <Button
                  onClick={() => {
                    setShowHistoryModal(false);
                    setCandidateDetail(null);
                  }}
                  variant="secondary"
                >
                  Close
                </Button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {candidateDetail.candidate.status_history.length === 0 ? (
                <p className="text-center text-gray-900 py-8">No status history available.</p>
              ) : (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Change History</h3>
                  {candidateDetail.candidate.status_history.map((item, index) => (
                    <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          {item.previous_status && (
                            <>
                              <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.previous_status_display || item.previous_status)}`}>
                                {item.previous_status_display || item.previous_status}
                              </span>
                              <span className="text-gray-900">→</span>
                            </>
                          )}
                          <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.new_status_display)}`}>
                            {item.new_status_display}
                          </span>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-900 font-medium">
                            {format(new Date(item.changed_at), 'MMM dd, yyyy')}
                          </p>
                          <p className="text-sm text-gray-900">
                            {format(new Date(item.changed_at), 'HH:mm')}
                          </p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-900">Changed by:</span>
                          <span className="ml-2 text-gray-900">{item.changed_by}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-900">Change #{candidateDetail.candidate.status_history.length - index}</span>
                        </div>
                      </div>
                      
                      {item.comments && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-md">
                          <p className="font-medium text-gray-900 text-sm mb-1">Comments:</p>
                          <p className="text-gray-900 text-sm">{item.comments}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}