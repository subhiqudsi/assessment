"""
Django management command to populate the database with test data.
Usage: python manage.py populate_candidates [--count 100000] [--batch-size 1000]
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from datetime import date, timedelta
import random
from faker import Faker
from io import BytesIO
from django.core.files.base import ContentFile

from job_application.models import Candidate, Department, ApplicationStatus, StatusHistory

class Command(BaseCommand):
    help = 'Populate database with fake candidate data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100000,
            help='Number of candidates to create (default: 100000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing candidates before populating'
        )

    def handle(self, *args, **options):
        count = options['count']
        batch_size = 10000
        clear_data = options['clear']
        
        fake = Faker()

        self.stdout.write(
            self.style.SUCCESS(f'Starting to populate {count:,} candidates...')
        )
        
        if clear_data:
            self.stdout.write('Clearing existing candidates...')
            print(Candidate.objects.all().delete())
            self.stdout.write(self.style.WARNING('Existing data cleared.'))
            return
        # Create one dummy resume file to be shared by all candidates
        pdf_header = b'%PDF-1.4\n'
        dummy_resume_content = f"""
RESUME

Name: Sample Candidate
Email: sample@example.com
Phone: +1-555-0123

EXPERIENCE:
{fake.text(max_nb_chars=500)}

EDUCATION:
{fake.text(max_nb_chars=200)}

SKILLS:
{fake.text(max_nb_chars=150)}
""".encode('utf-8')

        dummy_resume_data = pdf_header + dummy_resume_content
        dummy_resume_file = ContentFile(
            dummy_resume_data,
            name="dummy_resume.pdf"
        )

        def generate_batch_data(size):
            """Generate fake candidate data in batches for better performance"""
            data = []
            
            # Pre-calculate choices
            dept_choices = [dept[0] for dept in Department.choices]
            status_choices = [status[0] for status in ApplicationStatus.choices]
            min_age, max_age = 18, 65
            
            for _ in range(size):
                # Generate realistic birth date (18-65 years old)
                birth_date = fake.date_between(
                    start_date=date.today() - timedelta(days=max_age*365),
                    end_date=date.today() - timedelta(days=min_age*365)
                )
                
                # Calculate realistic years of experience
                age = (date.today() - birth_date).days // 365
                max_experience = max(0, age - 18)
                years_experience = random.randint(0, min(max_experience, 40))
                
                # Generate unique identifiers
                email_base = fake.user_name()
                domain = fake.free_email_domain()
                email = f"{email_base}_{random.randint(1000, 9999)}@{domain}"
                phone = fake.phone_number()[:20]
                
                data.append({
                    'full_name': fake.name(),
                    'email': email,
                    'phone_number': phone,
                    'date_of_birth': birth_date,
                    'years_of_experience': years_experience,
                    'department': random.choice(dept_choices),
                    'status': random.choice(status_choices),
                })
            
            return data

        created_count = 0
        batch_count = 0
        
        try:
            while created_count < count:
                remaining = min(batch_size, count - created_count)
                candidates = []
                
                self.stdout.write(f'Creating batch {batch_count + 1}: {created_count + 1}-{created_count + remaining}')
                
                # Generate batch data efficiently
                candidate_data_list = generate_batch_data(remaining)
                
                # Create candidates with shared dummy resume file for performance
                for candidate_data in candidate_data_list:
                    candidate = Candidate(
                        full_name=candidate_data['full_name'],
                        email=candidate_data['email'],
                        phone_number=candidate_data['phone_number'],
                        date_of_birth=candidate_data['date_of_birth'],
                        years_of_experience=candidate_data['years_of_experience'],
                        department=candidate_data['department'],
                        status=candidate_data['status'],
                        resume=dummy_resume_file
                    )
                    candidates.append(candidate)
                
                # Bulk create candidates
                if candidates:
                    with transaction.atomic():
                        created_candidates = Candidate.objects.bulk_create(
                            candidates,
                            ignore_conflicts=True,
                            batch_size=500
                        )
                        
                        batch_created = len(created_candidates)
                        created_count += batch_created
                        batch_count += 1
                        
                        # Create some status histories in bulk
                        if batch_count % 10 == 0:
                            status_histories = []
                            for candidate in created_candidates:
                                status_histories.append(StatusHistory(
                                    candidate=candidate,
                                    previous_status=None,
                                    new_status=candidate.status,
                                    comments="Initial application",
                                    changed_by="system"
                                ))
                            try:
                                StatusHistory.objects.bulk_create(status_histories, ignore_conflicts=True)
                            except Exception:
                                pass
                        
                        # Only show progress every 5 batches to reduce I/O
                        if batch_count % 5 == 0:
                            progress = (created_count / count) * 100
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✓ Batches {batch_count-4}-{batch_count} complete: '
                                    f'(Total: {created_count:,}/{count:,} - {progress:.1f}%)'
                                )
                            )
                
                # Progress checkpoint
                if created_count % 10000 == 0 and created_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f'📊 Checkpoint: {created_count:,} candidates created')
                    )
        
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.ERROR(f'\n⚠️  Interrupted! Created {created_count:,} candidates.')
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            return
        
        # Final statistics
        total_in_db = Candidate.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Population complete!')
        )
        self.stdout.write(f'📈 Created: {created_count:,} candidates')
        self.stdout.write(f'📊 Total in database: {total_in_db:,}')
        
        # Show distribution
        self.stdout.write('\n📋 Department distribution:')
        for dept_code, dept_name in Department.choices:
            dept_count = Candidate.objects.filter(department=dept_code).count()
            percentage = (dept_count / total_in_db * 100) if total_in_db > 0 else 0
            self.stdout.write(f'  {dept_name}: {dept_count:,} ({percentage:.1f}%)')
        
        self.stdout.write('\n📋 Status distribution:')
        for status_code, status_name in ApplicationStatus.choices:
            status_count = Candidate.objects.filter(status=status_code).count()
            percentage = (status_count / total_in_db * 100) if total_in_db > 0 else 0
            self.stdout.write(f'  {status_name}: {status_count:,} ({percentage:.1f}%)')