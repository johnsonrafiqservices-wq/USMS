from collections import OrderedDict

from django import forms
from django.contrib.auth.models import Permission
from django.utils.safestring import mark_safe


class GroupedPermissionsWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        value = [str(v) for v in value]

        permissions = Permission.objects.select_related('content_type').order_by(
            'content_type__app_label', 'content_type__model', 'codename'
        )

        grouped = OrderedDict()
        for perm in permissions:
            app = perm.content_type.app_label
            if app not in grouped:
                grouped[app] = []
            grouped[app].append(perm)

        app_display = {
            'admin': 'Admin',
            'auth': 'Authentication and Authorization',
            'contenttypes': 'Content Types',
            'sessions': 'Sessions',
            'jet': 'Jet',
            'accounts': 'Accounts',
            'students': 'Students',
            'academics': 'Academics',
            'staff': 'Staff',
            'finance': 'Finance',
            'library': 'Library',
            'hostel': 'Hostel',
            'communications': 'Communications',
        }

        app_icons = {
            'admin': 'bi-shield-lock',
            'auth': 'bi-key-fill',
            'contenttypes': 'bi-diagram-3',
            'sessions': 'bi-clock-history',
            'jet': 'bi-speedometer2',
            'accounts': 'bi-person-badge',
            'students': 'bi-mortarboard',
            'academics': 'bi-book',
            'staff': 'bi-person-workspace',
            'finance': 'bi-cash-stack',
            'library': 'bi-journal-bookmark',
            'hostel': 'bi-building',
            'communications': 'bi-megaphone',
        }

        app_colors = {
            'admin': '#475569',
            'auth': '#2563eb',
            'contenttypes': '#64748b',
            'sessions': '#64748b',
            'jet': '#0d9488',
            'accounts': '#1e3a5f',
            'students': '#2563eb',
            'academics': '#d97706',
            'staff': '#059669',
            'finance': '#db2777',
            'library': '#7c3aed',
            'hostel': '#0891b2',
            'communications': '#ea580c',
        }

        widget_id = attrs.get('id', 'id_user_permissions') if attrs else 'id_user_permissions'

        html = []
        html.append(
            '<style>'
            '.grouped-permissions-widget { width:100% !important; }'
            '.field-user_permissions .related-widget-wrapper,'
            '.field-user_permissions .flex-container,'
            '.field-user_permissions > div,'
            '#user_permissions-group .flex-container,'
            'fieldset .form-row.field-user_permissions > div { '
            '  width:100% !important; max-width:100% !important; '
            '}'
            '</style>'
        )
        html.append(
            f'<div id="{widget_id}_grouped" class="grouped-permissions-widget" '
            f'style="width:100%;display:grid;grid-template-columns:1fr 1fr;gap:6px 10px;">'
        )

        html.append(
            '<div style="grid-column:1/-1;margin-bottom:8px;display:flex;gap:8px;align-items:center;width:100%;">'
            f'<button type="button" class="btn btn-outline-primary btn-sm" onclick="gpwSelectAll(\'{widget_id}_grouped\')">Select All</button>'
            f'<button type="button" class="btn btn-outline-secondary btn-sm" onclick="gpwDeselectAll(\'{widget_id}_grouped\')">Deselect All</button>'
            f'<input type="text" class="form-control form-control-sm" placeholder="Search permissions..." '
            f'oninput="gpwSearch(this, \'{widget_id}_grouped\')" style="max-width:280px;margin-left:auto;">'
            '</div>'
        )

        for app_label, perms in grouped.items():
            display_name = app_display.get(app_label, app_label.replace('_', ' ').title())
            icon = app_icons.get(app_label, 'bi-app')
            color = app_colors.get(app_label, '#64748b')
            selected_count = sum(1 for p in perms if str(p.pk) in value)
            total_count = len(perms)
            section_id = f'{widget_id}_{app_label}'

            html.append(f'<div class="gpw-section" data-app="{app_label}" style="min-width:0;">')
            html.append(
                f'<div class="gpw-header" onclick="gpwToggle(\'{section_id}\')" '
                f'style="cursor:pointer;display:flex;align-items:center;gap:10px;'
                f'padding:10px 16px;background:#f8fafc;border:1px solid #e2e8f0;'
                f'border-radius:8px;transition:all .15s;width:100%;box-sizing:border-box;"'
                f' onmouseover="this.style.background=\'#f1f5f9\'" onmouseout="this.style.background=\'#f8fafc\'">'
                f'<i class="bi {icon}" style="color:{color};font-size:16px;"></i>'
                f'<span style="font-weight:700;font-size:13px;color:#1e293b;flex:1;">{display_name}</span>'
                f'<span class="gpw-count" id="{section_id}_count" style="font-size:11px;font-weight:600;'
                f'padding:2px 8px;border-radius:10px;'
                f'background:{"#dbeafe" if selected_count > 0 else "#f1f5f9"};'
                f'color:{"#2563eb" if selected_count > 0 else "#94a3b8"};"'
                f'>{selected_count}/{total_count}</span>'
                f'<i class="bi bi-chevron-down gpw-chevron" id="{section_id}_chevron" '
                f'style="font-size:12px;color:#94a3b8;transition:transform .2s;"></i>'
                '</div>'
            )

            html.append(
                f'<div class="gpw-body" id="{section_id}" '
                f'style="display:none;padding:10px 16px 14px 16px;border:1px solid #e2e8f0;'
                f'border-top:none;border-radius:0 0 8px 8px;background:#fff;'
                f'width:100%;box-sizing:border-box;">'
            )

            html.append(
                f'<label style="display:flex;align-items:center;gap:6px;padding:4px 0 8px 0; width:100%;'
                f'border-bottom:1px solid #f1f5f9;margin-bottom:6px;cursor:pointer;font-size:12px;'
                f'font-weight:600;color:{color};">'
                f'<input type="checkbox" onchange="gpwToggleApp(this, \'{section_id}\')" '
                f'{"checked" if selected_count == total_count and total_count > 0 else ""}>'
                f' Select all {display_name}'
                '</label>'
            )

            html.append('<div style="display:grid;grid-template-columns:1fr 1fr;gap:0 24px;width:100%;">')
            for perm in perms:
                perm_id = f'{widget_id}_{perm.pk}'
                checked = 'checked' if str(perm.pk) in value else ''
                perm_label = f'{perm.content_type.model} &middot; {perm.name}'
                html.append(
                    f'<label class="gpw-perm" style="display:flex;align-items:center;gap:8px; width:100%;'
                    f'padding:4px 0;font-size:12px;color:#374151;cursor:pointer;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" '
                    f'data-search="{perm.codename} {perm.name} {perm.content_type.model}"'
                    f' title="{perm.content_type.app_label} | {perm.content_type.model} | {perm.name}">'
                    f'<input type="checkbox" name="{name}" value="{perm.pk}" '
                    f'id="{perm_id}" {checked} onchange="gpwUpdateCount(\'{section_id}\')" '
                    f'style="flex-shrink:0;">'
                    f'<span style="white-space:nowrap;">{perm_label}</span>'
                    '</label>'
                )
            html.append('</div>')

            html.append('</div>')
            html.append('</div>')

        html.append('</div>')

        html.append('''
<script>
function gpwToggle(sectionId) {
    const body = document.getElementById(sectionId);
    const chevron = document.getElementById(sectionId + '_chevron');
    const section = body.closest('.gpw-section');
    if (body.style.display === 'none') {
        body.style.display = 'block';
        chevron.style.transform = 'rotate(180deg)';
        if (section) section.style.gridColumn = '1 / -1';
    } else {
        body.style.display = 'none';
        chevron.style.transform = 'rotate(0deg)';
        if (section) section.style.gridColumn = 'auto';
    }
}

function gpwUpdateCount(sectionId) {
    const body = document.getElementById(sectionId);
    const countEl = document.getElementById(sectionId + '_count');
    if (!body || !countEl) return;
    const checks = body.querySelectorAll('input[type="checkbox"][name]');
    const checked = Array.from(checks).filter(c => c.checked).length;
    const total = checks.length;
    countEl.textContent = checked + '/' + total;
    countEl.style.background = checked > 0 ? '#dbeafe' : '#f1f5f9';
    countEl.style.color = checked > 0 ? '#2563eb' : '#94a3b8';
    const appToggle = body.querySelector('input[type="checkbox"]:not([name])');
    if (appToggle) appToggle.checked = (checked === total && total > 0);
}

function gpwToggleApp(masterCheckbox, sectionId) {
    const body = document.getElementById(sectionId);
    const checks = body.querySelectorAll('input[type="checkbox"][name]');
    checks.forEach(c => c.checked = masterCheckbox.checked);
    gpwUpdateCount(sectionId);
}

function gpwSelectAll(widgetId) {
    const widget = document.getElementById(widgetId);
    widget.querySelectorAll('input[type="checkbox"]').forEach(c => c.checked = true);
    widget.querySelectorAll('.gpw-section').forEach(sec => {
        const sectionId = sec.querySelector('.gpw-body')?.id;
        if (sectionId) gpwUpdateCount(sectionId);
    });
}

function gpwDeselectAll(widgetId) {
    const widget = document.getElementById(widgetId);
    widget.querySelectorAll('input[type="checkbox"]').forEach(c => c.checked = false);
    widget.querySelectorAll('.gpw-section').forEach(sec => {
        const sectionId = sec.querySelector('.gpw-body')?.id;
        if (sectionId) gpwUpdateCount(sectionId);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.grouped-permissions-widget').forEach(function(widget) {
        let el = widget.parentElement;
        while (el && !el.matches('#content, #content-main, body')) {
            el.style.width = '100%';
            el.style.maxWidth = '100%';
            el = el.parentElement;
        }
    });
});

function gpwSearch(input, widgetId) {
    const query = input.value.toLowerCase().trim();
    const widget = document.getElementById(widgetId);
    widget.querySelectorAll('.gpw-section').forEach(sec => {
        const body = sec.querySelector('.gpw-body');
        const perms = sec.querySelectorAll('.gpw-perm');
        let anyVisible = false;
        perms.forEach(p => {
            const text = (p.getAttribute('data-search') || p.textContent).toLowerCase();
            const match = !query || text.includes(query);
            p.style.display = match ? 'flex' : 'none';
            if (match) anyVisible = true;
        });
        sec.style.display = anyVisible ? 'block' : 'none';
        if (query && anyVisible && body) {
            body.style.display = 'block';
            const chevron = document.getElementById(body.id + '_chevron');
            if (chevron) chevron.style.transform = 'rotate(180deg)';
        }
    });
}
</script>
''')

        return mark_safe('\n'.join(html))
