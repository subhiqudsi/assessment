import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const adminApi = axios.create({
  baseURL: `${API_URL}/admin`,
  headers: {
    'Content-Type': 'application/json',
    'X-ADMIN': '1',
  },
});

export interface Candidate {
  id: number;
  full_name: string;
  date_of_birth: string;
  years_of_experience: number;
  department: 'IT' | 'HR' | 'Finance';
  status?: string;
  created_at?: string;
}

export interface CandidateRegistration {
  full_name: string;
  date_of_birth: string;
  years_of_experience: number;
  department: 'IT' | 'HR' | 'Finance';
  resume: File;
}

export interface ApplicationStatus {
  id: number;
  status: string;
  updated_at: string;
  feedback?: string;
}