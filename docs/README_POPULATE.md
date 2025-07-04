# Database Population Scripts

This directory contains scripts to populate the database with test data for performance testing.

## 🚀 Quick Start

### Django Management Command (Recommended)

```bash
# Populate with 100,000 records (default)
docker-compose exec web python manage.py populate_candidates

# Populate with custom count
docker-compose exec web python manage.py populate_candidates --count 50000

# Clear existing data and populate
docker-compose exec web python manage.py populate_candidates --count 100000 --clear
```

## 📊 Performance Testing

The scripts create realistic test data:

- **Candidates**: Random names, emails, phone numbers
- **Demographics**: Ages 18-65 with realistic experience levels
- **Departments**: Even distribution across IT, HR, Finance
- **Status**: Random application statuses
- **Resume Files**: Mock PDF files with realistic content
- **Status History**: Sample status change records

## ⚡ Performance Optimizations

- **Bulk Operations**: Uses `bulk_create()` for faster inserts
- **Batch Processing**: Processes records in configurable batches
- **Memory Management**: Commits data periodically to prevent memory issues
- **Conflict Handling**: Ignores duplicate entries gracefully

## 🔧 Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--count` | 100,000 | Number of candidates to create |
| `--clear` | False | Clear existing data first |

## 📈 Expected Performance

On typical hardware:
- **1,000 records**: ~25 seconds
- **10,000 records**: ~4 minutes
- **100,000 records**: ~40 minutes

## 🧪 Testing the Results

After population, test the API performance:

```bash
# Test pagination
curl "http://localhost:8000/api/admin/candidates/?page=1&page_size=20" -H "X-ADMIN: 1"

# Test filtering
curl "http://localhost:8000/api/admin/candidates/?department=IT&page_size=50" -H "X-ADMIN: 1"

# Test search
curl "http://localhost:8000/api/admin/candidates/?search=john&page_size=10" -H "X-ADMIN: 1"

# Check total count
docker-compose exec web python manage.py shell -c "from job_application.models import Candidate; print(f'Total candidates: {Candidate.objects.count():,}')"
```

## 📋 Generated Data Examples

**Candidate Data:**
- Names: "John Smith", "Maria Garcia", etc.
- Emails: "user_1234@example.com"
- Phones: Various realistic formats
- Birth Dates: 1959-2006 (ages 18-65)
- Experience: 0-40 years (realistic for age)
- Departments: IT, HR, Finance
- Status: All application statuses

**Resume Files:**
- PDF format with headers
- Contains candidate info and sample content
- Stored in structured paths: `resumes/{candidate_id}/`

## 🛠 Troubleshooting

**Memory Issues:**
```bash
# Reduce batch size
python manage.py populate_candidates --batch-size 500
```

**Disk Space:**
- 100K records ≈ 2-3 GB (including resume files)
- Monitor available disk space

**Performance:**
- Database indexes are optimized for large datasets
- Pagination prevents memory issues in API responses

## 🧹 Cleanup

To remove test data:
```bash
docker-compose exec web python manage.py shell -c "from job_application.models import Candidate; Candidate.objects.all().delete(); print('All candidates deleted')"
```