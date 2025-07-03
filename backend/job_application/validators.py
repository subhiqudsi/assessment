from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
import magic
import logging

logger = logging.getLogger('hr_system')

# Maximum file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'application/pdf': ['pdf'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
    'application/msword': ['doc'],  # Legacy support
}

# File signatures (magic numbers) for additional security
FILE_SIGNATURES = {
    b'%PDF': 'pdf',
    b'PK\x03\x04': 'docx',  # DOCX files are ZIP archives
    b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'doc',  # Legacy DOC format
}


def validate_resume_file(file: UploadedFile):
    """
    Comprehensive file validation for resume uploads
    Validates file size, extension, MIME type, and file signature
    """
    if not file:
        raise ValidationError("No file provided.")

    # Validate file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024 * 1024)}MB. "
            f"Your file is {file.size // (1024 * 1024)}MB."
        )

    # Get file extension from filename
    filename = file.name.lower() if file.name else ''
    if not filename:
        raise ValidationError("File must have a valid filename.")

    file_extension = filename.split('.')[-1] if '.' in filename else ''
    if file_extension not in ['pdf', 'docx', 'doc']:
        raise ValidationError(
            f"Invalid file extension '{file_extension}'. "
            "Only PDF and DOCX files are allowed."
        )

    # Validate MIME type
    try:
        # Reset file pointer to beginning
        file.seek(0)

        # Use python-magic to detect MIME type
        mime_type = magic.from_buffer(file.read(1024), mime=True)

        # Reset file pointer again
        file.seek(0)

        if mime_type not in ALLOWED_MIME_TYPES:
            logger.warning(
                f"Invalid MIME type detected: {mime_type} for file {filename}"
            )
            raise ValidationError(
                f"Invalid file type. Only PDF and DOCX files are allowed. "
                f"Detected type: {mime_type}"
            )

        # Check if extension matches MIME type
        expected_extensions = ALLOWED_MIME_TYPES[mime_type]
        if file_extension not in expected_extensions:
            logger.warning(
                f"File extension mismatch: {file_extension} vs expected {expected_extensions} "
                f"for MIME type {mime_type}"
            )
            raise ValidationError(
                f"File extension '{file_extension}' does not match file content type."
            )

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Error validating file {filename}: {str(e)}")
        raise ValidationError("Unable to validate file. Please ensure it's a valid PDF or DOCX file.")

    # Additional file signature validation
    try:
        file.seek(0)
        file_header = file.read(8)  # Read first 8 bytes
        file.seek(0)  # Reset again

        signature_valid = False
        for signature, file_type in FILE_SIGNATURES.items():
            if file_header.startswith(signature):
                if file_type in ['pdf', 'docx', 'doc'] and file_extension in ['pdf', 'docx', 'doc']:
                    signature_valid = True
                break

        if not signature_valid:
            logger.warning(
                f"Invalid file signature for {filename}. Header: {file_header[:4]}"
            )
            raise ValidationError(
                "File appears to be corrupted or not a valid PDF/DOCX file."
            )

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Error checking file signature for {filename}: {str(e)}")
        # Don't fail the validation if signature check fails, just log it
        pass

    # Log successful validation
    logger.info(f"File validation successful: {filename} ({file.size} bytes, {mime_type})")

    return file


def validate_file_content_safety(file: UploadedFile):
    """
    Additional safety checks for file content
    This is a placeholder for more advanced security checks
    """
    try:
        file.seek(0)

        # Basic check for suspicious content in filenames
        suspicious_patterns = [
            '../', '..\\', '.exe', '.bat', '.cmd', '.scr', '.vbs',
            '<script', 'javascript:', 'data:', 'vbscript:'
        ]

        filename_lower = file.name.lower() if file.name else ''
        for pattern in suspicious_patterns:
            if pattern in filename_lower:
                raise ValidationError(
                    "Filename contains potentially unsafe characters or patterns."
                )

        # Check for minimum file size (empty files)
        if file.size < 100:  # Less than 100 bytes is suspicious for a resume
            raise ValidationError("File appears to be empty or too small to be a valid resume.")

        file.seek(0)  # Reset file pointer

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"Error in content safety validation: {str(e)}")
        # Don't fail validation for safety check errors, just log them
        pass

    return file


def validate_candidate_data_integrity(candidate_data):
    """
    Validate candidate data for consistency and integrity
    """
    errors = {}

    # Validate name format
    full_name = candidate_data.get('full_name', '').strip()
    if full_name:
        if len(full_name) < 2:
            errors['full_name'] = "Full name must be at least 2 characters long."
        elif len(full_name) > 255:
            errors['full_name'] = "Full name is too long (maximum 255 characters)."
        elif not any(c.isalpha() for c in full_name):
            errors['full_name'] = "Full name must contain at least one letter."

    # Validate email format (additional to Django's EmailField validation)
    email = candidate_data.get('email', '').strip().lower()
    if email:
        if len(email) > 254:  # RFC 5321 limit
            errors['email'] = "Email address is too long."

        # Check for suspicious patterns
        suspicious_domains = ['example.com', 'test.com', 'localhost']
        domain = email.split('@')[-1] if '@' in email else ''
        if domain in suspicious_domains:
            errors['email'] = "Please use a valid email address."

    # Validate phone number format
    phone = candidate_data.get('phone_number', '').strip()
    if phone:
        # Remove common separators
        phone_digits = ''.join(c for c in phone if c.isdigit())
        if len(phone_digits) < 7:
            errors['phone_number'] = "Phone number is too short."
        elif len(phone_digits) > 15:  # ITU-T E.164 standard
            errors['phone_number'] = "Phone number is too long."

    # Validate years of experience consistency
    years_exp = candidate_data.get('years_of_experience')
    date_of_birth = candidate_data.get('date_of_birth')

    if years_exp is not None and date_of_birth:
        # Convert years_exp to int if it's a string
        try:
            years_exp = int(years_exp)
        except (ValueError, TypeError):
            errors['years_of_experience'] = "Years of experience must be a valid integer."
            return candidate_data
        from datetime import date
        # Handle different date formats
        if isinstance(date_of_birth, str):
            try:
                from datetime import datetime
                date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                errors['date_of_birth'] = "Invalid date format. Use YYYY-MM-DD."
                return candidate_data
        
        today = date.today()
        age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )

        # Check if years of experience is reasonable for the age
        max_reasonable_exp = max(0, age - 16)  # Assuming work starts at 16
        if years_exp > max_reasonable_exp:
            errors['years_of_experience'] = (
                f"Years of experience ({years_exp}) seems unrealistic for age ({age}). "
                f"Maximum reasonable experience would be {max_reasonable_exp} years."
            )

    if errors:
        raise ValidationError(errors)

    return candidate_data