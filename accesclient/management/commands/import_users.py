import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings

class Command(BaseCommand):
    help = 'Import users from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing users')

    def handle(self, *args, **options):
        json_file_path = options['json_file']

        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
            return

        with open(json_file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Check if the JSON has a "rows" key (based on the file structure)
                if isinstance(data, dict) and 'rows' in data:
                    users_data = data['rows']
                elif isinstance(data, list):
                    users_data = data
                else:
                    self.stdout.write(self.style.ERROR('Invalid JSON structure: Expected a list or a dict with "rows" key'))
                    return
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON: {e}'))
                return

        count_created = 0
        count_updated = 0

        for item in users_data:
            username = item.get('NomBaseDick')
            last_name = item.get('NomClient')
            password = item.get('MdpClear')
            email = item.get('MailContact')

            if not username:
                self.stdout.write(self.style.WARNING(f'Skipping user with no NomBaseDick: {item}'))
                continue

            # Ensure username is unique or get existing
            user, created = User.objects.get_or_create(username=username)

            user.last_name = last_name if last_name else ''
            
            if email:
                user.email = email
            
            # Set password
            if password:
                user.set_password(password)
            
            # Set is_active = 1 (True)
            user.is_active = True
            
            user.save()

            if created:
                count_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                count_updated += 1
                self.stdout.write(self.style.SUCCESS(f'Updated user: {username}'))

        self.stdout.write(self.style.SUCCESS(f'Import complete. Created: {count_created}, Updated: {count_updated}'))
