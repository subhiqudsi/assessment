# HR System Frontend

A Next.js application for the HR Management System that allows candidates to apply for positions and HR managers to review applications.

## Features

### For Candidates
- Register and submit job applications
- Upload resume (PDF or DOCX, max 5MB)
- Track application status using candidate ID
- View status history and feedback

### For HR Managers
- Admin dashboard to view all candidates
- Filter candidates by department
- Download candidate resumes
- Update application status with feedback
- Paginated candidate list

## Tech Stack
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- React Hook Form
- Axios for API calls
- date-fns for date formatting

## Getting Started

### Prerequisites
- Node.js 18+ installed
- Backend API running on http://localhost:8000

### Installation

1. Navigate to the project directory:
```bash
cd frontend/hr-system
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file (already created with default values):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. Run the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## Project Structure

```
hr-system/
├── app/                    # Next.js app directory
│   ├── admin/             # Admin pages
│   │   ├── login/         # Admin login
│   │   └── dashboard/     # Admin dashboard
│   ├── candidate/         # Candidate pages
│   │   ├── register/      # Registration form
│   │   └── status/        # Status check
│   └── page.tsx           # Home page
├── components/            # Reusable components
│   └── ui/               # UI components
├── lib/                   # API client and utilities
├── hooks/                 # Custom React hooks
└── utils/                 # Constants and helpers
```

## Usage

### Candidate Registration
1. Navigate to the home page
2. Click "Apply Now"
3. Fill out the form with:
   - Full Name
   - Date of Birth
   - Years of Experience
   - Department (IT, HR, or Finance)
   - Resume file (PDF or DOCX)
4. Submit the application
5. Save the candidate ID for status tracking

### Check Application Status
1. Click "Check Application Status"
2. Enter your candidate ID
3. View current status and history

### Admin Access
1. View and manage candidates
2. Download resumes
3. Update application statuses

## Development

### Build for Production
```bash
npm run build
```

### Run Production Build
```bash
npm start
```

### Linting
```bash
npm run lint
```

## Notes
- Admin authentication is simplified for this demo (using local state)
- File uploads are handled via multipart/form-data
- The application is responsive and works on mobile devices
- Error handling and loading states are implemented throughout
