"""Import database from JSON file."""
import json
from django.core.management.base import BaseCommand
from django.core import serializers
import sys


class Command(BaseCommand):
    help = 'Import database from a JSON file exported by export_db'

    def add_arguments(self, parser):
        parser.add_argument(
            'input_file',
            type=str,
            help='Input JSON file path to import',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import (use with caution)',
        )

    def handle(self, *args, **options):
        input_file = options.get('input_file')
        clear_first = options.get('clear', False)
        
        if not input_file:
            self.stdout.write(self.style.ERROR('Input file path is required'))
            return
        
        try:
            # Read JSON file
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                self.stdout.write(self.style.WARNING('No data found in file'))
                return
            
            # Optionally clear existing data (DANGER)
            if clear_first:
                confirm = input(
                    'WARNING: This will delete all existing data! Type "yes" to confirm: '
                )
                if confirm.lower() == 'yes':
                    from django.apps import apps
                    for model in apps.get_models():
                        if model._meta.app_label not in ['contenttypes', 'auth', 'sessions']:
                            model.objects.all().delete()
                    self.stdout.write(self.style.WARNING('Cleared existing data'))
                else:
                    self.stdout.write('Cancelled')
                    return
            
            # Deserialize and save data
            for obj in serializers.deserialize('json', json.dumps(data)):
                obj.save()
            
            record_count = len(data)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {record_count} records from {input_file}'
                )
            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {input_file}'))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))
            raise
