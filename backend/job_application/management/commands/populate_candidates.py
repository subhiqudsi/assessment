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
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk operations (default: 1000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing candidates before populating'
        )

    def handle(self, *args, **options):
        count = options['count']
        batch_size = options['batch_size']
        clear_data = options['clear']
        
        fake = Faker()
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting to populate {count:,} candidates...')
        )
        
        if clear_data:
            self.stdout.write('Clearing existing candidates...')
            Candidate.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing data cleared.'))
        
        def create_fake_resume_content():
            """Create fake PDF-like content for testing"""
            pdf_header = b'%PDF-1.4\n'
            fake_content = f"""
RESUME

Name: {fake.name()}
Email: {fake.email()}
Phone: {fake.phone_number()}

EXPERIENCE:
{fake.text(max_nb_chars=500)}

EDUCATION:
{fake.text(max_nb_chars=200)}

SKILLS:
{fake.text(max_nb_chars=150)}
""".encode('utf-8')
            return pdf_header + fake_content

        def generate_candidate_data():
            """Generate fake candidate data"""
            # Generate realistic birth date (18-65 years old)
            min_age, max_age = 18, 65
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
            
            return {
                'full_name': fake.name(),
                'email': email,
                'phone_number': phone,
                'date_of_birth': birth_date,
                'years_of_experience': years_experience,
                'department': random.choice([dept[0] for dept in Department.choices]),
                'status': random.choice([status[0] for status in ApplicationStatus.choices]),
            }

        created_count = 0
        batch_count = 0
        
        try:
            while created_count < count:
                remaining = min(batch_size, count - created_count)
                candidates = []
                
                self.stdout.write(f'Creating batch {batch_count + 1}: {created_count + 1}-{created_count + remaining}')
                
                for i in range(remaining):
                    try:
                        candidate_data = generate_candidate_data()
                        
                        # Create fake resume
                        resume_content = create_fake_resume_content()
                        resume_file = ContentFile(
                            resume_content,
                            name=f"resume_{batch_count}_{i}_{random.randint(1000, 9999)}.pdf"
                        )
                        
                        candidate = Candidate(
                            full_name=candidate_data['full_name'],
                            email=candidate_data['email'],
                            phone_number=candidate_data['phone_number'],
                            date_of_birth=candidate_data['date_of_birth'],
                            years_of_experience=candidate_data['years_of_experience'],
                            department=candidate_data['department'],
                            status=candidate_data['status'],
                            resume=resume_file
                        )
                        candidates.append(candidate)
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error creating candidate {i}: {str(e)}')
                        )
                        continue
                
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
                        
                        # Create some status histories
                        if batch_count % 10 == 0:
                            for candidate in created_candidates[:20]:
                                try:
                                    StatusHistory.objects.create(
                                        candidate=candidate,
                                        previous_status=None,
                                        new_status=candidate.status,
                                        comments="Initial application",
                                        changed_by="system"
                                    )
                                except:
                                    pass
                        
                        progress = (created_count / count) * 100
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Batch complete: {batch_created} candidates '
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