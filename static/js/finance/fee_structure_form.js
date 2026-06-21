// Initializes the fee structure multi-step form loaded into the quick-create modal.
// Call as `initFeeStructureForm(root)` where `root` is an element containing the form (optional).
(function () {
    window.initFeeStructureForm = function(root) {
        const scope = root && root.querySelector ? root : document;
        // State
        let currentStep = 1;
        const totalSteps = 5;

        // Helper functions (scoped queries)
        function qs(sel) { return scope.querySelector(sel); }
        function qsa(sel) { return Array.from(scope.querySelectorAll(sel)); }

        function getSelectedFacultyIds() {
            const facultyCheckboxes = qsa('.faculty-checkbox');
            const selected = [];
            facultyCheckboxes.forEach(cb => { if (cb.checked) selected.push(parseInt(cb.dataset.facultyId)); });
            return selected;
        }

        function getSelectedProgramIds() {
            const programmeItems = qsa('.programme-item');
            const selected = [];
            programmeItems.forEach(item => {
                const cb = item.querySelector('.prog-checkbox');
                if (cb && cb.checked && item.style.display !== 'none') selected.push(parseInt(cb.value));
            });
            return selected;
        }

        function getSelectedDepartmentIds() {
            const departmentItems = qsa('.department-item');
            const selected = [];
            departmentItems.forEach(item => {
                const cb = item.querySelector('.dept-checkbox');
                if (cb && cb.checked && item.style.display !== 'none') selected.push(parseInt(cb.value));
            });
            return selected;
        }

        function updateStepIndicators() {
            qsa('.step-indicator').forEach(indicator => {
                const step = parseInt(indicator.dataset.step);
                const circle = indicator.querySelector('.step-circle');
                const label = indicator.querySelector('.step-label');
                if (!circle || !label) return;
                if (step === currentStep) {
                    circle.classList.remove('bg-secondary');
                    circle.classList.add('bg-primary');
                    label.classList.remove('text-muted');
                    label.classList.add('fw-bold');
                } else if (step < currentStep) {
                    circle.classList.remove('bg-secondary', 'bg-primary');
                    circle.classList.add('bg-success');
                    label.classList.remove('text-muted', 'fw-bold');
                } else {
                    circle.classList.remove('bg-primary', 'bg-success');
                    circle.classList.add('bg-secondary');
                    label.classList.remove('fw-bold');
                    label.classList.add('text-muted');
                }
            });
        }

        function updateProgrammes() {
            const selectedFacultyIds = getSelectedFacultyIds();
            const programmeItems = qsa('.programme-item');
            const totalFaculties = qsa('.faculty-checkbox').length;
            programmeItems.forEach(item => {
                const facultyId = parseInt(item.dataset.facultyId);
                if (selectedFacultyIds.includes(facultyId)) item.style.display = 'block';
                else { item.style.display = 'none'; const cb = item.querySelector('.prog-checkbox'); if (cb) cb.checked = false; }
            });
            const allProgrammesCheck = qs('#allProgrammesCheck');
            const progDivider = qs('#progDivider');
            if (allProgrammesCheck) {
                if (selectedFacultyIds.length === totalFaculties) { allProgrammesCheck.style.display = 'block'; if (progDivider) progDivider.style.display = 'block'; }
                else { allProgrammesCheck.style.display = 'none'; if (progDivider) progDivider.style.display = 'none'; const prog_all = qs('#prog_all'); if (prog_all) prog_all.checked = false; }
            }
            updateDepartments();
        }

        function updateDepartments() {
            const selectedFacultyIds = getSelectedFacultyIds();
            const departmentItems = qsa('.department-item');
            departmentItems.forEach(item => {
                const facultyId = parseInt(item.dataset.facultyId);
                if (selectedFacultyIds.includes(facultyId)) item.style.display = 'block';
                else { item.style.display = 'none'; const cb = item.querySelector('.dept-checkbox'); if (cb) cb.checked = false; }
            });
            const allDepartmentsCheck = qs('#allDepartmentsCheck');
            const deptDivider = qs('#deptDivider');
            if (allDepartmentsCheck) {
                if (selectedFacultyIds.length > 0) { allDepartmentsCheck.style.display = 'block'; if (deptDivider) deptDivider.style.display = 'block'; }
                else { allDepartmentsCheck.style.display = 'none'; if (deptDivider) deptDivider.style.display = 'none'; const dept_all = qs('#dept_all'); if (dept_all) dept_all.checked = false; }
            }
            updateCourses();
        }

        function updateCourses() {
            const selectedDepartmentIds = getSelectedDepartmentIds();
            const courseItems = qsa('.course-item');
            courseItems.forEach(item => {
                const departmentId = parseInt(item.dataset.departmentId);
                if (selectedDepartmentIds.includes(departmentId)) item.style.display = 'block';
                else { item.style.display = 'none'; const cb = item.querySelector('.course-checkbox'); if (cb) cb.checked = false; }
            });
            const allCoursesCheck = qs('#allCoursesCheck');
            const courseDivider = qs('#courseDivider');
            if (allCoursesCheck) {
                if (selectedDepartmentIds.length > 0) { allCoursesCheck.style.display = 'block'; if (courseDivider) courseDivider.style.display = 'block'; }
                else { allCoursesCheck.style.display = 'none'; if (courseDivider) courseDivider.style.display = 'none'; const course_all = qs('#course_all'); if (course_all) course_all.checked = false; }
            }
        }

        function goToNextStep() {
            if (currentStep < totalSteps) {
                if (currentStep === 1 && getSelectedFacultyIds().length === 0) { alert('Please select at least one faculty'); return; }
                if (currentStep === 2 && getSelectedProgramIds().length === 0) { alert('Please select at least one program'); return; }
                if (currentStep === 3 && getSelectedDepartmentIds().length === 0) { alert('Please select at least one department'); return; }
                const cur = qs(`.step-content[data-step="${currentStep}"]`); if (cur) cur.style.display = 'none';
                currentStep++; const nxt = qs(`.step-content[data-step="${currentStep}"]`); if (nxt) nxt.style.display = 'block';
                updateStepIndicators();
            }
        }

        function goToPrevStep() {
            if (currentStep > 1) {
                const cur = qs(`.step-content[data-step="${currentStep}"]`); if (cur) cur.style.display = 'none';
                currentStep--; const prev = qs(`.step-content[data-step="${currentStep}"]`); if (prev) prev.style.display = 'block';
                updateStepIndicators();
            }
        }

        // Event delegation for buttons
        function onClick(e) {
            const form = e.target.closest('#feeForm');
            if (!form) return;
            if (e.target.closest('[data-action="next-step"]')) { e.preventDefault(); goToNextStep(); }
            if (e.target.closest('[data-action="prev-step"]')) { e.preventDefault(); goToPrevStep(); }
        }

        function onChange(e) {
            const form = e.target.closest('#feeForm'); if (!form) return;
            if (e.target.classList.contains('faculty-checkbox')) {
                const facultyAllCheckbox = qs('#fac_all'); const facultyCheckboxes = qsa('.faculty-checkbox');
                const selectedCount = getSelectedFacultyIds().length; if (facultyAllCheckbox) facultyAllCheckbox.checked = selectedCount === facultyCheckboxes.length; updateProgrammes();
            }
            if (e.target.id === 'fac_all') { const facultyCheckboxes = qsa('.faculty-checkbox'); if (e.target.checked) facultyCheckboxes.forEach(cb=>cb.checked=true); else facultyCheckboxes.forEach(cb=>cb.checked=false); updateProgrammes(); }
            if (e.target.id === 'prog_all') { const programmeItems = qsa('.programme-item'); if (e.target.checked) programmeItems.forEach(item=>{ if (item.style.display!=='none'){ const cb = item.querySelector('.prog-checkbox'); if(cb)cb.checked=true; } }) ; else programmeItems.forEach(item=>{ const cb = item.querySelector('.prog-checkbox'); if(cb)cb.checked=false; }); }
            if (e.target.id === 'dept_all') { const departmentItems = qsa('.department-item'); if (e.target.checked) departmentItems.forEach(item=>{ if (item.style.display!=='none'){ const cb = item.querySelector('.dept-checkbox'); if(cb)cb.checked=true; } }) ; else departmentItems.forEach(item=>{ const cb = item.querySelector('.dept-checkbox'); if(cb)cb.checked=false; }); updateCourses(); }
            if (e.target.classList.contains('dept-checkbox')) updateCourses();
            if (e.target.id === 'course_all') { const courseItems = qsa('.course-item'); if (e.target.checked) courseItems.forEach(item=>{ if (item.style.display!=='none'){ const cb = item.querySelector('.course-checkbox'); if(cb)cb.checked=true; } }) ; else courseItems.forEach(item=>{ const cb = item.querySelector('.course-checkbox'); if(cb)cb.checked=false; }); }
        }

        // Attach listeners (avoid duplicate handlers)
        document.removeEventListener('click', onClick);
        document.addEventListener('click', onClick);
        document.removeEventListener('change', onChange);
        document.addEventListener('change', onChange);

        // Initialize visibility
        const form = qs('#feeForm');
        if (form) {
            updateProgrammes(); updateDepartments(); updateCourses(); updateStepIndicators();
        }
    };
})();
