# Serializer Unit Tests Summary

This document provides an overview of the unit tests created for the job application serializers.

## Test Coverage

### 1. CandidateRegistrationSerializerTestCase
Tests for the serializer used to register new candidates.

- **test_valid_data_serialization**: Validates that correct data passes validation
- **test_create_candidate**: Verifies candidate creation with initial status history
- **test_duplicate_email_validation**: Ensures duplicate emails are rejected
- **test_duplicate_phone_validation**: Ensures duplicate phone numbers are rejected
- **test_years_of_experience_validation**: Tests negative and excessive experience values
- **test_invalid_file_extension**: Validates that only PDF and DOCX files are accepted
- **test_all_fields_required**: Confirms all fields are mandatory

### 2. CandidateStatusSerializerTestCase
Tests for the serializer used to check candidate status.

- **test_serialization**: Validates all fields are properly serialized
- **test_latest_feedback_none**: Handles cases with no status history
- **test_read_only_fields**: Confirms all fields are read-only

### 3. StatusHistorySerializerTestCase
Tests for the status history tracking serializer.

- **test_serialization**: Validates proper serialization of history entries
- **test_null_previous_status**: Handles initial status entries

### 4. AdminCandidateListSerializerTestCase
Tests for the admin list view serializer.

- **test_serialization**: Validates all list fields
- **test_age_calculation**: Verifies age is calculated correctly
- **test_has_resume_false**: Tests resume existence checking

### 5. AdminCandidateDetailSerializerTestCase
Tests for the detailed admin view serializer.

- **test_serialization_includes_history**: Confirms status history is included
- **test_resume_filename_extraction**: Validates filename extraction
- **test_no_resume_filename**: Handles missing resumes

### 6. StatusUpdateSerializerTestCase
Tests for the status update functionality.

- **test_valid_status_update**: Validates correct status updates
- **test_same_status_validation**: Prevents redundant status changes
- **test_update_status_method**: Tests the complete update flow with notifications
- **test_notification_failure_handling**: Ensures updates work even if notifications fail
- **test_optional_fields**: Confirms comments and changed_by are optional

### 7. DepartmentFilterSerializerTestCase
Tests for department filtering.

- **test_valid_department**: Validates correct department values
- **test_optional_department**: Confirms department is optional
- **test_blank_department**: Allows blank department values
- **test_invalid_department**: Rejects invalid department choices

## Key Testing Patterns

1. **Mock Usage**: External dependencies like logging and notifications are mocked
2. **Edge Cases**: Tests cover null values, missing data, and error scenarios
3. **Validation**: Comprehensive validation testing for all business rules
4. **File Handling**: Proper PDF file headers used to avoid MIME type warnings
5. **Read-Only Fields**: Verification that read-only fields cannot be modified

## Running the Tests

To run these tests in the Docker environment:

```bash
docker-compose exec web python manage.py test job_application.test_serializers -v 2
```

All 27 tests pass successfully with a total runtime of approximately 0.087 seconds.