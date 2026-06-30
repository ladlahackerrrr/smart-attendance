/**
 * AttendAI — Attendance Marking Client-Side Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  const deptSelect = document.getElementById('deptSelect');
  const programSelect = document.getElementById('programSelect');
  const semSelect = document.getElementById('semSelect');
  const sectionSelect = document.getElementById('sectionSelect');
  const subjectSelect = document.getElementById('subjectSelect');
  const dateInput = document.getElementById('dateInput');
  const form = document.getElementById('attendanceSelectForm');

  const studentRollCard = document.getElementById('studentRollCard');
  const selectPromptState = document.getElementById('selectPromptState');
  const studentGrid = document.getElementById('studentGrid');
  const rollClassName = document.getElementById('rollClassName');
  const attendanceCounters = document.getElementById('attendanceCounters');

  const markAllPresentBtn = document.getElementById('markAllPresentBtn');
  const markAllAbsentBtn = document.getElementById('markAllAbsentBtn');
  const saveAttendanceBtn = document.getElementById('saveAttendanceBtn');
  const cancelMarkingBtn = document.getElementById('cancelMarkingBtn');

  let currentStudents = []; // Store list of student statuses

  // ── 1. CASCADING SELECTORS ──

  if (deptSelect) {
    deptSelect.addEventListener('change', async () => {
      const deptId = deptSelect.value;
      resetSelect(programSelect, 'program');
      resetSelect(semSelect, 'semester');
      resetSelect(sectionSelect, 'section');
      resetSelect(subjectSelect, 'subject');

      if (!deptId) return;

      try {
        const data = await Utils.fetchJSON(`/api/programs/${deptId}`);
        populateSelect(programSelect, data, 'name');
        programSelect.disabled = false;
      } catch (e) {
        Notifications.showToast('Failed to load programs', 'error');
      }
    });
  }

  if (programSelect) {
    programSelect.addEventListener('change', async () => {
      const progId = programSelect.value;
      resetSelect(semSelect, 'semester');
      resetSelect(sectionSelect, 'section');
      resetSelect(subjectSelect, 'subject');

      if (!progId) return;

      try {
        const data = await Utils.fetchJSON(`/api/semesters/${progId}`);
        populateSelect(semSelect, data, 'label');
        semSelect.disabled = false;
      } catch (e) {
        Notifications.showToast('Failed to load semesters', 'error');
      }
    });
  }

  if (semSelect) {
    semSelect.addEventListener('change', async () => {
      const semId = semSelect.value;
      resetSelect(sectionSelect, 'section');
      resetSelect(subjectSelect, 'subject');

      if (!semId) return;

      try {
        const data = await Utils.fetchJSON(`/api/sections/${semId}`);
        populateSelect(sectionSelect, data, 'name');
        sectionSelect.disabled = false;
      } catch (e) {
        Notifications.showToast('Failed to load sections', 'error');
      }
    });
  }

  if (sectionSelect) {
    sectionSelect.addEventListener('change', async () => {
      const secId = sectionSelect.value;
      resetSelect(subjectSelect, 'subject');

      if (!secId) return;

      try {
        const data = await Utils.fetchJSON(`/api/subjects/${secId}`);
        // Map the options manually since custom object fields exist
        subjectSelect.innerHTML = '<option value="">Choose subject...</option>';
        data.forEach(item => {
          const opt = document.createElement('option');
          opt.value = item.section_subject_id;
          opt.textContent = `${item.name} (${item.code}) — ${item.teacher_name}`;
          subjectSelect.appendChild(opt);
        });
        subjectSelect.disabled = false;
      } catch (e) {
        Notifications.showToast('Failed to load subjects', 'error');
      }
    });
  }

  function resetSelect(selectEl, label) {
    selectEl.innerHTML = `<option value="">Choose ${label}...</option>`;
    selectEl.disabled = true;
  }

  function populateSelect(selectEl, list, displayField) {
    selectEl.innerHTML = `<option value="">Choose ${selectEl.id.replace('Select', '')}...</option>`;
    list.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item.id;
      opt.textContent = item[displayField];
      selectEl.appendChild(opt);
    });
  }

  // ── 2. LOAD STUDENT REGISTRY ──

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const sectionId = sectionSelect.value;
      const sectionSubjectId = subjectSelect.value;
      const dateVal = dateInput.value;

      if (!sectionId || !sectionSubjectId || !dateVal) return;

      Utils.showLoading(studentRollCard);
      studentRollCard.classList.remove('d-none');
      selectPromptState.classList.add('d-none');

      try {
        const data = await Utils.fetchJSON(`/api/students/${sectionId}?section_subject_id=${sectionSubjectId}&date=${dateVal}`);
        currentStudents = data.map(s => ({
          student_id: s.id,
          name: s.name,
          roll_number: s.roll_number,
          status: s.status || 'present' // default to present if none registered
        }));
        
        // Update Title details
        const selectedSubName = subjectSelect.options[subjectSelect.selectedIndex].textContent.split(' — ')[0];
        rollClassName.textContent = `${selectedSubName} • Date: ${dateVal}`;

        renderStudentList();
        updateCounters();
      } catch (err) {
        Notifications.showToast('Failed to load student rolls', 'error');
      } finally {
        Utils.hideLoading(studentRollCard);
      }
    });
  }

  // ── 3. RENDERING & INTERACTIONS ──

  function renderStudentList() {
    studentGrid.innerHTML = '';

    if (currentStudents.length === 0) {
      studentGrid.innerHTML = `
        <div class="col-12 text-center py-4">
          <i class="bi bi-people text-muted fs-3"></i>
          <p class="text-muted mb-0 mt-1">No students registered in this section.</p>
        </div>
      `;
      return;
    }

    currentStudents.forEach(student => {
      const col = document.createElement('div');
      col.className = 'col-md-6 col-lg-4';
      
      const isPresent = student.status === 'present';
      
      col.innerHTML = `
        <div class="attendance-toggle ${isPresent ? 'present' : 'absent'} px-3 py-2 cursor-pointer" data-id="${student.student_id}">
          <div class="toggle-indicator"></div>
          <div class="flex-grow-1 overflow-hidden">
            <div class="fw-semibold text-truncate" style="font-size:0.85rem;">${student.name}</div>
            <small class="text-muted font-mono" style="font-size:0.75rem;">${student.roll_number}</small>
          </div>
          <span class="badge ${isPresent ? 'bg-success bg-opacity-10 text-success' : 'bg-danger bg-opacity-10 text-danger'}" style="font-size:0.7rem;">
            ${isPresent ? 'Present' : 'Absent'}
          </span>
        </div>
      `;

      // Toggle action click
      const card = col.querySelector('.attendance-toggle');
      card.addEventListener('click', () => {
        const studentId = student.student_id;
        const currentStatus = student.status;
        const newStatus = currentStatus === 'present' ? 'absent' : 'present';
        
        student.status = newStatus;
        
        // update visual styles
        card.className = `attendance-toggle ${newStatus} px-3 py-2 cursor-pointer`;
        const badge = card.querySelector('.badge');
        badge.className = `badge ${newStatus === 'present' ? 'bg-success bg-opacity-10 text-success' : 'bg-danger bg-opacity-10 text-danger'}`;
        badge.textContent = newStatus === 'present' ? 'Present' : 'Absent';
        
        updateCounters();
      });

      studentGrid.appendChild(col);
    });
  }

  function updateCounters() {
    const total = currentStudents.length;
    const present = currentStudents.filter(s => s.status === 'present').length;
    const absent = total - present;
    attendanceCounters.textContent = `${present} Present • ${absent} Absent • ${total} Total`;
  }

  // Bulk actions
  if (markAllPresentBtn) {
    markAllPresentBtn.addEventListener('click', () => {
      currentStudents.forEach(s => s.status = 'present');
      renderStudentList();
      updateCounters();
    });
  }

  if (markAllAbsentBtn) {
    markAllAbsentBtn.addEventListener('click', () => {
      currentStudents.forEach(s => s.status = 'absent');
      renderStudentList();
      updateCounters();
    });
  }

  if (cancelMarkingBtn) {
    cancelMarkingBtn.addEventListener('click', () => {
      studentRollCard.classList.add('d-none');
      selectPromptState.classList.remove('d-none');
      currentStudents = [];
    });
  }

  // ── 4. SAVE BATCH TO DB ──

  if (saveAttendanceBtn) {
    saveAttendanceBtn.addEventListener('click', async () => {
      const sectionSubjectId = subjectSelect.value;
      const dateVal = dateInput.value;

      if (!sectionSubjectId || !dateVal || currentStudents.length === 0) return;

      Utils.showLoading(studentRollCard);

      try {
        const payload = {
          section_subject_id: parseInt(sectionSubjectId),
          date: dateVal,
          records: currentStudents.map(s => ({
            student_id: s.student_id,
            status: s.status
          }))
        };

        await Utils.fetchJSON('/api/attendance/save', {
          method: 'POST',
          body: payload
        });

        Notifications.showToast('Attendance saved successfully!', 'success');
        
        // Hide roll and reset selector form
        setTimeout(() => {
          studentRollCard.classList.add('d-none');
          selectPromptState.classList.remove('d-none');
          currentStudents = [];
        }, 1000);

      } catch (err) {
        Notifications.showToast(err.message || 'Failed to save attendance records', 'error');
      } finally {
        Utils.hideLoading(studentRollCard);
      }
    });
  }
});
