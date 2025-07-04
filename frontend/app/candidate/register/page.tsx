'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { api } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { DEPARTMENTS } from '@/utils/constants';

interface FormData {
  full_name: string;
  email: string;
  phone_number: string;
  date_of_birth: string;
  years_of_experience: string;
  department: string;
  resume: FileList;
}

export default function CandidateRegister() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [candidateId, setCandidateId] = useState<number | null>(null);
  const [submittedEmail, setSubmittedEmail] = useState<string>('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('full_name', data.full_name);
      formData.append('email', data.email);
      formData.append('phone_number', data.phone_number);
      formData.append('date_of_birth', data.date_of_birth);
      formData.append('years_of_experience', data.years_of_experience);
      formData.append('department', data.department);
      formData.append('resume', data.resume[0]);

      const response = await api.post('/candidates/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setCandidateId(response.data.candidate_id);
      setSubmittedEmail(data.email);
    } catch (err: any) {
      if (err.response?.data?.errors) {
        // Handle validation errors
        const errors = err.response.data.errors;
        const errorMessages = Object.entries(errors).map(([field, messages]: [string, any]) => 
          `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
        ).join('\n');
        setError(`Validation failed:\n${errorMessages}`);
      } else {
        setError(err.response?.data?.message || err.response?.data?.detail || 'An error occurred during registration');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (candidateId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
          <div className="mb-4">
            <svg
              className="w-16 h-16 text-green-500 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Registration Successful!</h2>
          <p className="text-gray-900 mb-6">
            Your application has been submitted successfully. Your candidate ID is: <strong>{candidateId}</strong>
          </p>
          <p className="text-sm text-gray-900 mb-6">
            Please save this ID to check your application status later.
          </p>
          <div className="space-y-3">
            <Button
              onClick={() => router.push(`/candidate/status?email=${encodeURIComponent(submittedEmail)}`)}
              className="w-full"
            >
              Check Application Status
            </Button>
            <Button
              onClick={() => router.push('/')}
              variant="secondary"
              className="w-full"
            >
              Return to Homepage
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Candidate Registration</h1>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6">
              <pre className="whitespace-pre-wrap text-sm">{error}</pre>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <Input
              label="Full Name"
              {...register('full_name', { required: 'Full name is required' })}
              error={errors.full_name?.message}
            />

            <Input
              label="Email"
              type="email"
              {...register('email', { 
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address'
                }
              })}
              error={errors.email?.message}
            />

            <Input
              label="Phone Number"
              type="tel"
              {...register('phone_number', { required: 'Phone number is required' })}
              error={errors.phone_number?.message}
            />

            <Input
              label="Date of Birth"
              type="date"
              {...register('date_of_birth', { required: 'Date of birth is required' })}
              error={errors.date_of_birth?.message}
            />

            <Input
              label="Years of Experience"
              type="number"
              min="0"
              {...register('years_of_experience', {
                required: 'Years of experience is required',
                min: { value: 0, message: 'Years of experience must be positive' },
              })}
              error={errors.years_of_experience?.message}
            />

            <Select
              label="Department"
              options={DEPARTMENTS}
              {...register('department', { required: 'Department is required' })}
              error={errors.department?.message}
            />

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-900 mb-1">
                Resume (PDF or DOCX, max 5MB)
              </label>
              <input
                type="file"
                accept=".pdf,.docx"
                {...register('resume', {
                  required: 'Resume is required',
                  validate: {
                    fileType: (files) => {
                      if (!files[0]) return true;
                      const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
                      return allowedTypes.includes(files[0].type) || 'Only PDF and DOCX files are allowed';
                    },
                    fileSize: (files) => {
                      if (!files[0]) return true;
                      return files[0].size <= 5 * 1024 * 1024 || 'File size must be less than 5MB';
                    },
                  },
                })}
                className="w-full px-3 py-2 border-2 border-gray-400 bg-white text-gray-900 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {errors.resume && <p className="mt-1 text-sm text-red-600">{errors.resume.message}</p>}
            </div>

            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? 'Submitting...' : 'Submit Application'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}