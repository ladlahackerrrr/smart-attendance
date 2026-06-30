/**
 * AttendAI — Notifications & Toast System
 */

const Notifications = {
  /**
   * Create and show a custom toast notification
   */
  showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    // Toast markup
    const toast = document.createElement('div');
    toast.className = `toast show ${type} align-items-center border-0 shadow-sm mb-2`;
    toast.role = 'alert';
    toast.ariaLive = 'assertive';
    toast.ariaAtomic = 'true';

    let icon = 'bi-info-circle-fill';
    if (type === 'success') icon = 'bi-check-circle-fill text-success';
    if (type === 'error' || type === 'danger') icon = 'bi-exclamation-triangle-fill text-danger';
    if (type === 'warning') icon = 'bi-exclamation-circle-fill text-warning';

    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${icon} fs-5"></i>
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;

    container.appendChild(toast);

    // Auto dismiss
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  /**
   * Fetch recent notifications and update Navbar badge
   */
  async loadDropdownNotifications() {
    const list = document.getElementById('notificationsList');
    const badge = document.getElementById('notifBadge');
    if (!list) return;

    try {
      const data = await Utils.fetchJSON('/api/notifications');
      
      // Update badge
      const unreadCount = data.filter(n => !n.is_read).length;
      if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'block';
      } else {
        badge.style.display = 'none';
      }

      if (data.length === 0) {
        list.innerHTML = `
          <div class="text-center py-4">
            <i class="bi bi-bell-slash text-muted fs-2"></i>
            <p class="text-muted mb-0 mt-2" style="font-size:0.85rem;">No new notifications</p>
          </div>
        `;
        return;
      }

      list.innerHTML = data.map(n => `
        <div class="dropdown-item px-3 py-2 border-bottom d-flex align-items-start gap-2 ${n.is_read ? '' : 'bg-light bg-opacity-50'}" style="white-space:normal; cursor:pointer;" onclick="Notifications.markRead(${n.id}, '${n.link || '#'}')">
          <div class="flex-shrink-0 mt-1">
            ${n.type === 'alert' ? '<i class="bi bi-exclamation-triangle-fill text-danger"></i>' :
              n.type === 'warning' ? '<i class="bi bi-exclamation-circle-fill text-warning"></i>' :
              n.type === 'success' ? '<i class="bi bi-check-circle-fill text-success"></i>' :
              '<i class="bi bi-info-circle-fill text-primary"></i>'}
          </div>
          <div class="flex-grow-1">
            <div class="fw-semibold text-dark" style="font-size:0.82rem;">${n.title}</div>
            <div class="text-muted" style="font-size:0.75rem;">${n.message}</div>
            <small class="text-muted" style="font-size:0.65rem;">${n.created_at}</small>
          </div>
          ${n.is_read ? '' : '<span class="status-dot online flex-shrink-0 mt-2"></span>'}
        </div>
      `).join('');

    } catch (e) {
      console.error("Failed to load notifications", e);
    }
  },

  /**
   * Mark a notification as read and redirect
   */
  async markRead(id, redirectUrl) {
    try {
      await Utils.fetchJSON(`/api/notifications/read/${id}`, { method: 'POST' });
      if (redirectUrl && redirectUrl !== '#') {
        window.location.href = redirectUrl;
      } else {
        this.loadDropdownNotifications();
      }
    } catch (e) {
      console.error(e);
      if (redirectUrl && redirectUrl !== '#') {
        window.location.href = redirectUrl;
      }
    }
  },

  /**
   * Mark all read
   */
  async markAllRead() {
    try {
      await Utils.fetchJSON('/api/notifications/read-all', { method: 'POST' });
      this.loadDropdownNotifications();
      this.showToast('All notifications marked as read', 'success');
    } catch (e) {
      console.error(e);
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // Load initially
  Notifications.loadDropdownNotifications();

  // Mark all read listener
  const btn = document.getElementById('markAllReadBtn');
  if (btn) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      Notifications.markAllRead();
    });
  }

  // Refresh every 30 seconds
  setInterval(() => {
    Notifications.loadDropdownNotifications();
  }, 30000);
});
