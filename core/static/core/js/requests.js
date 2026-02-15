/**
 * Django WebRTC Invitation & Join Request System - Frontend JavaScript
 * 
 * Usage:
 * 1. Include this script in your template: <script src="{% static 'core/js/requests.js' %}"></script>
 * 2. Call the appropriate functions based on user role
 */

// ========== HELPER FUNCTIONS ==========

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        font-weight: 500;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;

    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    } else if (type === 'warning') {
        notification.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)';
    }

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// ========== PARTICIPANT FUNCTIONS ==========

/**
 * Poll invitations for the current user every 2 seconds
 * Shows modal when invitation received
 */
function startPollingInvitations() {
    function poll() {
        fetch('/api/my-invitations/', {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok' && data.invitations.length > 0) {
                showInvitationModal(data.invitations[0]);
            }
        })
        .catch(err => console.log('Poll invitations error:', err));
    }

    // Initial poll
    poll();
    // Poll every 2 seconds
    return setInterval(poll, 2000);
}

/**
 * Show modal for invitation
 */
function showInvitationModal(invitation) {
    // Check if modal already exists to avoid duplicates
    if (document.getElementById('invitationModal')) {
        return;
    }

    const modal = document.createElement('div');
    modal.id = 'invitationModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.95) 100%);
        border-radius: 16px;
        padding: 2rem;
        max-width: 400px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        border: 1px solid rgba(99,102,241,0.3);
    `;

    content.innerHTML = `
        <h2 style="margin: 0 0 1rem 0; font-size: 1.5rem; background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            New Invitation! 🎉
        </h2>
        <p style="margin: 1rem 0; color: rgba(255,255,255,0.8);">
            ${invitation.session__host__username} invited you to join session <strong>${invitation.session__room_code}</strong>
        </p>
        <div style="display: flex; gap: 1rem; margin-top: 2rem;">
            <button id="acceptBtn" style="flex: 1; padding: 0.75rem; border: none; border-radius: 8px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; cursor: pointer; font-weight: 600; transition: transform 0.2s;">
                Accept ✓
            </button>
            <button id="rejectBtn" style="flex: 1; padding: 0.75rem; border: none; border-radius: 8px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; cursor: pointer; font-weight: 600; transition: transform 0.2s;">
                Reject ✗
            </button>
        </div>
    `;

    modal.appendChild(content);
    document.body.appendChild(modal);

    document.getElementById('acceptBtn').addEventListener('click', () => {
        respondToInvitation(invitation.session__id, 'accepted');
        modal.remove();
    });

    document.getElementById('rejectBtn').addEventListener('click', () => {
        respondToInvitation(invitation.session__id, 'rejected');
        modal.remove();
    });
}

/**
 * Accept or reject an invitation
 */
function respondToInvitation(sessionId, action) {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('action', action);
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch('/api/respond-invite/', {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            const message = action === 'accepted' 
                ? 'Invitation accepted! Redirecting to session...' 
                : 'Invitation rejected.';
            showNotification(message, action === 'accepted' ? 'success' : 'info');
            
            if (action === 'accepted') {
                setTimeout(() => window.location.reload(), 1500);
            }
        } else {
            showNotification(data.error || 'Error processing invitation', 'error');
        }
    })
    .catch(err => {
        console.error('Response error:', err);
        showNotification('Failed to process invitation', 'error');
    });
}

/**
 * Join session with room code
 */
function joinWithCode(roomCode) {
    if (!roomCode.trim()) {
        showNotification('Please enter a room code', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('room_code', roomCode.trim());
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch('/api/join-with-code/', {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            showNotification(data.message, 'success');
            // Redirect to waiting room
            setTimeout(() => {
                window.location.href = `/session/${roomCode}/waiting/`;
            }, 1500);
        } else {
            showNotification(data.error || 'Failed to join session', 'error');
        }
    })
    .catch(err => {
        console.error('Join error:', err);
        showNotification('Error joining session', 'error');
    });
}

// ========== HOST FUNCTIONS ==========

/**
 * Poll pending join requests for host every 2 seconds
 */
function startPollingRequests(roomCode) {
    function poll() {
        fetch(`/api/session-requests/${roomCode}/`, {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                updateRequestsList(data.requests);
            }
        })
        .catch(err => console.log('Poll requests error:', err));
    }

    // Initial poll
    poll();
    // Poll every 2 seconds
    return setInterval(poll, 2000);
}

/**
 * Update the requests list in the DOM
 */
function updateRequestsList(requests) {
    const container = document.getElementById('requestsList');
    if (!container) return;

    if (requests.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.6);">No pending requests</p>';
        return;
    }

    container.innerHTML = requests.map(req => `
        <div style="background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.3); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>${req.user__username}</strong>
                <p style="margin: 0.25rem 0 0; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                    ${new Date(req.joined_at).toLocaleString()}
                </p>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <button class="btn-approve" data-username="${req.user__username}" style="padding: 0.5rem 1rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border: none; border-radius: 6px; color: white; cursor: pointer; font-weight: 500;">
                    Approve
                </button>
                <button class="btn-reject" data-username="${req.user__username}" style="padding: 0.5rem 1rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border: none; border-radius: 6px; color: white; cursor: pointer; font-weight: 500;">
                    Reject
                </button>
            </div>
        </div>
    `).join('');

    // Attach event listeners
    document.querySelectorAll('.btn-approve').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const username = e.target.getAttribute('data-username');
            handleJoinRequest(username, 'accepted');
        });
    });

    document.querySelectorAll('.btn-reject').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const username = e.target.getAttribute('data-username');
            handleJoinRequest(username, 'rejected');
        });
    });
}

/**
 * Handle join request (approve or reject)
 */
function handleJoinRequest(username, action) {
    const roomCode = getCurrentRoomCode();
    
    // Get session ID from data attribute or fetch it
    const formData = new FormData();
    formData.append('username', username);
    formData.append('session_id', document.getElementById('sessionId')?.value || '');
    formData.append('action', action);
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch('/api/handle-request/', {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            showNotification(`${username} ${action === 'accepted' ? 'approved' : 'rejected'}`, 'success');
        } else {
            showNotification(data.error || 'Error handling request', 'error');
        }
    })
    .catch(err => {
        console.error('Handle request error:', err);
        showNotification('Failed to handle request', 'error');
    });
}

/**
 * Invite participant by username
 */
function inviteParticipant(username, sessionId) {
    if (!username.trim()) {
        showNotification('Please enter a username', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('username', username.trim());
    formData.append('session_id', sessionId);
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch('/api/invite/', {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            showNotification(data.message, 'success');
            // Clear input if exists
            const input = document.getElementById('inviteUsername');
            if (input) input.value = '';
        } else {
            showNotification(data.error || 'Failed to send invitation', 'error');
        }
    })
    .catch(err => {
        console.error('Invite error:', err);
        showNotification('Error sending invitation', 'error');
    });
}

/**
 * Get current room code from URL or data attribute
 */
function getCurrentRoomCode() {
    const match = window.location.pathname.match(/\/session\/([^/]+)/);
    return match ? match[1] : null;
}

// Add CSS animation definitions to document
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    button:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
`;
document.head.appendChild(style);
