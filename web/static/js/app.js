// AI CCTV Surveillance Frontend Controller

let activeEnrollmentUserId = null;
let isEnrolling = false;

document.addEventListener("DOMContentLoaded", () => {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);

    // Initial data fetch
    fetchStatus();
    loadUsers();
    loadIntruderLogs();

    // Periodic status & logs polling
    setInterval(fetchStatus, 1500);
    setInterval(loadIntruderLogs, 4000);
});

function updateLiveClock() {
    const now = new Date();
    document.getElementById("liveClock").innerText = now.toLocaleTimeString() + " // SYS ARMED";
}

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        // Update badges
        document.getElementById("fpsBadge").innerText = `FPS: ${data.fps}`;
        document.getElementById("facesBadge").innerText = `FACES: ${data.total_faces}`;
        document.getElementById("userCountBadge").innerText = data.registered_users;

        // Threat status badge
        const threatBadge = document.getElementById("threatBadge");
        if (data.unauthorized_count > 0) {
            threatBadge.className = "badge bg-danger text-light px-3 py-2 border border-danger fa-beat";
            threatBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation me-1"></i> BREACH: ${data.unauthorized_count} INTRUDER(S)`;
        } else if (data.authorized_count > 0) {
            threatBadge.className = "badge bg-success text-light px-3 py-2 border border-success";
            threatBadge.innerHTML = `<i class="fa-solid fa-circle-check me-1"></i> ACCESS GRANTED`;
        } else {
            threatBadge.className = "badge bg-success-subtle text-success border border-success px-3 py-2";
            threatBadge.innerHTML = `<i class="fa-solid fa-shield-halved me-1"></i> STATUS: SECURE`;
        }

        // Voice state button
        const voiceText = document.getElementById("voiceBtnText");
        const voiceBtn = document.getElementById("toggleVoiceBtn");
        if (data.voice_enabled) {
            voiceText.innerText = "Voice: ON";
            voiceBtn.className = "btn btn-sm btn-outline-warning";
        } else {
            voiceText.innerText = "Voice: MUTED";
            voiceBtn.className = "btn btn-sm btn-secondary";
        }

        // DIP state button
        const dipText = document.getElementById("dipBtnText");
        const dipBtn = document.getElementById("toggleDipBtn");
        if (data.is_dip_mode) {
            dipText.innerText = "Return to CCTV HUD";
            dipBtn.className = "btn btn-sm btn-info";
        } else {
            dipText.innerText = "DIP Inspector (4-Way)";
            dipBtn.className = "btn btn-sm btn-outline-info";
        }
    } catch (err) {
        console.error("Status fetch error:", err);
    }
}

async function loadUsers() {
    try {
        const res = await fetch("/api/users");
        const data = await res.json();
        const container = document.getElementById("usersListContainer");
        const users = data.users || [];

        document.getElementById("userCountBadge").innerText = users.length;

        if (users.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-secondary">
                    <i class="fa-solid fa-user-slash fs-2 mb-2 d-block"></i>
                    No authorized personnel enrolled.<br>All detected faces will be marked as <span class="text-danger fw-bold">UNAUTHORIZED</span>.
                </div>
            `;
            return;
        }

        container.innerHTML = users.map(u => `
            <div class="user-card p-2 mb-2 d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center gap-2">
                    ${u.thumbnail 
                        ? `<img src="/${u.thumbnail}" class="user-thumb" alt="${u.name}">`
                        : `<div class="user-thumb bg-dark d-flex align-items-center justify-content-center text-secondary"><i class="fa-solid fa-user"></i></div>`
                    }
                    <div>
                        <div class="fw-bold text-light">${u.name}</div>
                        <div class="text-secondary" style="font-size: 0.78rem;">
                            <span class="text-info">${u.id}</span> | ${u.role} | ${u.sample_count} samples
                        </div>
                    </div>
                </div>
                <button class="btn btn-xs btn-outline-danger" onclick="revokeUser('${u.id}', '${u.name}')" title="Revoke Access">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `).join("");
    } catch (err) {
        console.error("Load users error:", err);
    }
}

async function loadIntruderLogs() {
    try {
        const res = await fetch("/api/intruders");
        const data = await res.json();
        const logs = data.logs || [];
        const container = document.getElementById("intrudersListContainer");
        document.getElementById("alertCountBadge").innerText = logs.length;

        if (logs.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-secondary">
                    <i class="fa-solid fa-shield-heart fs-2 mb-2 d-block text-success"></i>
                    No intruder security breaches recorded.
                </div>
            `;
            return;
        }

        container.innerHTML = logs.map(l => `
            <div class="intruder-card p-2 mb-2 d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center gap-2">
                    <a href="${l.snapshot_url}" target="_blank">
                        <img src="${l.snapshot_url}" class="intruder-thumb" alt="Intruder Snapshot">
                    </a>
                    <div>
                        <div class="fw-bold text-danger">
                            <i class="fa-solid fa-triangle-exclamation me-1"></i> UNAUTHORIZED INTRUSION
                        </div>
                        <div class="text-secondary" style="font-size: 0.78rem;">
                            ${l.timestamp} | ${l.camera}
                        </div>
                        <div class="text-warning" style="font-size: 0.75rem;">
                            Threat: ${l.threat_level} | Chi-Dist: ${l.avg_distance}
                        </div>
                    </div>
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Load intruders error:", err);
    }
}

async function toggleDipMode() {
    await fetch("/api/toggle_dip", { method: "POST" });
    fetchStatus();
}

async function toggleVoiceAlert() {
    await fetch("/api/toggle_voice", { method: "POST" });
    fetchStatus();
}

async function triggerRetrain() {
    const res = await fetch("/api/retrain", { method: "POST" });
    const data = await res.json();
    alert(data.message || "Model retrained!");
    loadUsers();
    fetchStatus();
}

async function revokeUser(userId, name) {
    if (!confirm(`Are you sure you want to revoke access permissions for ${name} (${userId})?`)) {
        return;
    }
    const res = await fetch(`/api/users/${userId}`, { method: "DELETE" });
    if (res.ok) {
        loadUsers();
        fetchStatus();
    }
}

async function clearIntruderLogs() {
    if (!confirm("Clear all recorded intruder evidence logs?")) return;
    await fetch("/api/clear_intruders", { method: "POST" });
    loadIntruderLogs();
}

// Enrollment Workflow
async function captureLiveSampleBurst() {
    const nameInput = document.getElementById("newUserName");
    const roleInput = document.getElementById("newUserRole");
    const name = nameInput.value.trim();
    const role = roleInput.value.trim() || "Authorized Personnel";

    if (!name) {
        alert("Please enter the person's full name first.");
        nameInput.focus();
        return;
    }

    const captureBtn = document.getElementById("startCaptureBtn");
    captureBtn.disabled = true;
    captureBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin me-1"></i> Capturing Face Samples...`;

    // 1. Create user if not created
    if (!activeEnrollmentUserId) {
        const createRes = await fetch("/api/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, role })
        });
        const createData = await createRes.json();
        if (!createData.success) {
            alert("Failed to initialize user: " + createData.error);
            captureBtn.disabled = false;
            captureBtn.innerHTML = "Capture 25 Face Samples";
            return;
        }
        activeEnrollmentUserId = createData.user.id;
    }

    // 2. Rapid multi-angle capture loop (25 samples)
    const targetSamples = 25;
    let successfulSamples = 0;
    const progressBar = document.getElementById("enrollmentProgressBar");
    const countDisplay = document.getElementById("sampleCountDisplay");

    for (let i = 0; i < targetSamples; i++) {
        const snapRes = await fetch("/api/capture_enrollment_sample", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: activeEnrollmentUserId })
        });
        const snapData = await snapRes.json();
        if (snapData.success) {
            successfulSamples = snapData.sample_count;
            const pct = Math.min(100, Math.round((successfulSamples / targetSamples) * 100));
            progressBar.style.width = pct + "%";
            countDisplay.innerText = `${successfulSamples} / ${targetSamples} Samples`;
        }
        // Small delay between frames for variation in pose and expression
        await new Promise(r => setTimeout(r, 180));
    }

    // 3. Automatically Retrain Model
    captureBtn.innerHTML = `<i class="fa-solid fa-microchip fa-spin me-1"></i> Training LBPH Recognizer...`;
    await fetch("/api/retrain", { method: "POST" });

    captureBtn.className = "btn btn-sm btn-success w-100";
    captureBtn.innerHTML = `<i class="fa-solid fa-check me-1"></i> Completed ${successfulSamples} Samples!`;
    loadUsers();
    fetchStatus();
}

async function uploadUserPhoto() {
    const nameInput = document.getElementById("newUserName");
    const roleInput = document.getElementById("newUserRole");
    const fileInput = document.getElementById("uploadPhotoInput");
    const name = nameInput.value.trim();
    const role = roleInput.value.trim() || "Authorized Personnel";

    if (!name) {
        alert("Please enter the person's full name first.");
        nameInput.focus();
        return;
    }
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please choose a photo file to upload.");
        return;
    }

    // Create user if not created
    if (!activeEnrollmentUserId) {
        const createRes = await fetch("/api/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, role })
        });
        const createData = await createRes.json();
        activeEnrollmentUserId = createData.user.id;
    }

    const formData = new FormData();
    formData.append("user_id", activeEnrollmentUserId);
    formData.append("photo", fileInput.files[0]);

    const res = await fetch("/api/upload_photo", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.success) {
        alert("Photo processed and LBPH model updated successfully!");
        loadUsers();
        fetchStatus();
    } else {
        alert(data.error || "Failed to process photo.");
    }
}

function finishEnrollment() {
    // Reset modal state
    activeEnrollmentUserId = null;
    document.getElementById("newUserName").value = "";
    document.getElementById("enrollmentProgressBar").style.width = "0%";
    document.getElementById("sampleCountDisplay").innerText = "0 / 25 Samples";
    const captureBtn = document.getElementById("startCaptureBtn");
    captureBtn.className = "btn btn-sm btn-outline-info w-100";
    captureBtn.disabled = false;
    captureBtn.innerHTML = `<i class="fa-solid fa-camera me-1"></i> Capture 25 Face Samples (Auto-Burst)`;

    const modal = bootstrap.Modal.getInstance(document.getElementById("addUserModal"));
    if (modal) modal.hide();
    loadUsers();
    fetchStatus();
}
