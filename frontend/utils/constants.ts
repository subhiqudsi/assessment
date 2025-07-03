export const DEPARTMENTS = [
  { value: 'IT', label: 'IT' },
  { value: 'HR', label: 'HR' },
  { value: 'Finance', label: 'Finance' },
] as const;

export const APPLICATION_STATUS = {
  SUBMITTED: 'Submitted',
  UNDER_REVIEW: 'Under Review',
  INTERVIEW_SCHEDULED: 'Interview Scheduled',
  REJECTED: 'Rejected',
  ACCEPTED: 'Accepted',
} as const;

export const STATUS_COLORS = {
  Submitted: 'bg-blue-100 text-blue-800',
  'Under Review': 'bg-yellow-100 text-yellow-800',
  'Interview Scheduled': 'bg-purple-100 text-purple-800',
  Rejected: 'bg-red-100 text-red-800',
  Accepted: 'bg-green-100 text-green-800',
} as const;