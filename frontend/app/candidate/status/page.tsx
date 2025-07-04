'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { STATUS_COLORS } from '@/utils/constants';
import { format } from 'date-fns';

interface ApplicationStatus {
  id: number;
  status: string;
  updated_at: string;
  feedback?: string;
  full_name: string;
  department: string;
  history?: {
    status: string;
    updated_at: string;
    feedback?: string;
  }[];
}

export default function CandidateStatus() {
  const searchParams = useSearchParams();
  const [email, setEmail] = useState(searchParams.get('email') || '');
  const [status, setStatus] = useState<ApplicationStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const checkStatus = async () => {
    if (!email) {
      setError('Please enter your email address');
      return;
    }

    setLoading(true);
    setError('');
    setStatus(null);

    try {
      const response = await api.get(`/candidates/status/?email=${encodeURIComponent(email)}`);
      setStatus(response.data.candidate);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch application status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (email) {
      checkStatus();
    }
  }, []);

  const getStatusColor = (status: string) => {
    return STATUS_COLORS[status as keyof typeof STATUS_COLORS] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Check Application Status</h1>

          <div className="flex gap-4 mb-8">
            <Input
              placeholder="Enter your email address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1"
            />
            <Button onClick={checkStatus} disabled={loading}>
              {loading ? 'Checking...' : 'Check Status'}
            </Button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6">
              {error}
            </div>
          )}

          {status && (
            <div className="space-y-6">
              <div className="border-b pb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Details</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-900">Full Name</p>
                    <p className="font-medium">{status.full_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-900">Department</p>
                    <p className="font-medium">{status.department}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-900">Candidate ID</p>
                    <p className="font-medium">{status.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-900">Current Status</p>
                    <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status.status)}`}>
                      {status.status}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Latest Update</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status.status)}`}>
                      {status.status}
                    </span>
                    <span className="text-sm text-gray-900">
                      {format(new Date(status.updated_at), 'MMM dd, yyyy HH:mm')}
                    </span>
                  </div>
                  {status.feedback && (
                    <p className="text-gray-900 mt-2">{status.feedback}</p>
                  )}
                </div>
              </div>

              {status.history && status.history.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Status History</h3>
                  <div className="space-y-3">
                    {status.history.map((item, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(item.status)}`}>
                            {item.status}
                          </span>
                          <span className="text-sm text-gray-900">
                            {format(new Date(item.updated_at), 'MMM dd, yyyy HH:mm')}
                          </span>
                        </div>
                        {item.feedback && (
                          <p className="text-gray-900 mt-2">{item.feedback}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}