"""Export database to JSON file."""
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps
import os


class Command(BaseCommand):
    help = 'Export the entire database to a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output file path (default: db_export_TIMESTAMP.json in media/backups)',
        )

    def handle(self, *args, **options):
        output_path = options.get('output')
        
        # Default to media/backups directory
        if not output_path:
            backups_dir = 'media/backups'
            if not os.path.exists(backups_dir):
                os.makedirs(backups_dir)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'{backups_dir}/db_export_{timestamp}.json'
        
        try:
            # Get all models from all apps
            all_data = []
            for model in apps.get_models():
                # Skip certain system models
                if model._meta.app_label in ['contenttypes', 'auth', 'sessions']:
                    continue
                
                queryset = model.objects.all()
                if queryset.exists():
                    serialized = serializers.serialize('json', queryset)
                    all_data.extend(json.loads(serialized))
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, default=str)
            
            record_count = len(all_data)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully exported {record_count} records to {output_path}'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Export failed: {str(e)}'))
            raise
