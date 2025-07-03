import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            HR Management System
          </h1>
          <p className="text-xl text-gray-600 mb-12">
            Apply for positions or manage applications
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">For Candidates</h2>
            <p className="text-gray-600 mb-6">
              Register and submit your application with your resume. Track your application status in real-time.
            </p>
            <div className="space-y-3">
              <Link href="/candidate/register" className="block">
                <Button className="w-full">Apply Now</Button>
              </Link>
              <Link href="/candidate/status" className="block">
                <Button variant="secondary" className="w-full">
                  Check Application Status
                </Button>
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">For HR Managers</h2>
            <p className="text-gray-600 mb-6">
              Access the admin dashboard to review candidates, download resumes, and manage application statuses.
            </p>
            <Link href="/admin/login" className="block">
              <Button className="w-full">Admin Login</Button>
            </Link>
          </div>
        </div>

        <div className="mt-16 text-center">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg p-6 shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4 mx-auto">
                <span className="text-blue-600 font-bold text-xl">1</span>
              </div>
              <h4 className="font-semibold mb-2">Submit Application</h4>
              <p className="text-gray-600 text-sm">
                Fill out your information and upload your resume in PDF or DOCX format
              </p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4 mx-auto">
                <span className="text-blue-600 font-bold text-xl">2</span>
              </div>
              <h4 className="font-semibold mb-2">Get Your ID</h4>
              <p className="text-gray-600 text-sm">
                Receive a unique candidate ID to track your application status
              </p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4 mx-auto">
                <span className="text-blue-600 font-bold text-xl">3</span>
              </div>
              <h4 className="font-semibold mb-2">Track Progress</h4>
              <p className="text-gray-600 text-sm">
                Check your application status anytime using your candidate ID
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
