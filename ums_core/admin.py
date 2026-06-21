from django.contrib.admin import AdminSite
from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.management import call_command
from django.utils.safestring import mark_safe
import tempfile
import os
from django.core.exceptions import PermissionDenied

class CustomAdminSite(AdminSite):
    """Custom admin site with automatic CSS loading."""
    site_header = 'University Management System'
    site_title = 'UMS Admin'
    index_title = 'Welcome to UMS Administration'

# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')


class ExportForm(forms.Form):
    zip = forms.BooleanField(required=False, label='Create ZIP archive')
    out = forms.CharField(required=False, label='Output filename', help_text='Optional absolute path or filename')


class ImportForm(forms.Form):
    file = forms.FileField(label='SQLite DB file')
    no_backup = forms.BooleanField(required=False, label='Do not back up existing DB')


def db_tools_view(request):
    """Admin view to export or import the project's SQLite DB."""
    # Allow only superusers or users with the 'ums_core.manage_db' permission
    if not (request.user.is_superuser or request.user.has_perm('ums_core.manage_db')):
        raise PermissionDenied('You do not have permission to access the database tools.')
    export_form = ExportForm(request.POST or None)
    import_form = ImportForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if 'export_submit' in request.POST and export_form.is_valid():
            zip_opt = export_form.cleaned_data.get('zip')
            out = export_form.cleaned_data.get('out') or None
            try:
                call_command('export_db', zip=zip_opt, out=out)
                messages.success(request, 'Database export completed. Check server output for path.')
            except Exception as e:
                messages.error(request, f'Export failed: {e}')
            return redirect(reverse('admin:db_tools'))

        if 'import_submit' in request.POST and import_form.is_valid():
            uploaded = import_form.cleaned_data['file']
            no_backup = import_form.cleaned_data.get('no_backup')
            try:
                tmp_path = None
                # save uploaded file to a temp location
                fd, tmp_path = tempfile.mkstemp(prefix='import_db_', suffix='.sqlite')
                with os.fdopen(fd, 'wb') as tmpf:
                    for chunk in uploaded.chunks():
                        tmpf.write(chunk)

                # call management command
                call_command('import_db', tmp_path, no_backup=no_backup)
                messages.success(request, 'Database import completed successfully.')
            except Exception as e:
                messages.error(request, f'Import failed: {e}')
            finally:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
            return redirect(reverse('admin:db_tools'))

    context = {
        'export_form': export_form,
        'import_form': import_form,
        'title': 'Database Import / Export',
    }
    return render(request, 'admin/db_tools.html', context)


# Expose the view name for urls.py imports
db_tools_view.__name__ = 'db_tools_view'
