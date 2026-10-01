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
    fetchTurretStatus();

    // Periodic status & logs polling
    setInterval(fetchStatus, 1500);
    setInterval(loadIntruderLogs, 4000);
    setInterval(fetchTurretStatus, 1500);
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

        // Turret navbar badge
        const turretNavBadge = document.getElementById("turretNavBadge");
        if (turretNavBadge) {
            if (data.turret_laser && data.turret_target_locked) {
                turretNavBadge.className = "badge bg-danger text-light px-2 py-2 border border-danger fa-beat";
                turretNavBadge.innerHTML = `<i class="fa-solid fa-bolt me-1"></i> LASER: FIRING (${data.turret_pan}°, ${data.turret_tilt}°)`;
            } else if (data.turret_connected) {
                turretNavBadge.className = "badge bg-success-subtle text-success border border-success px-2 py-2 font-monospace";
                turretNavBadge.innerHTML = `<i class="fa-solid fa-crosshairs me-1"></i> TURRET: ${data.turret_port}`;
            } else {
                turretNavBadge.className = "badge bg-dark border border-secondary text-secondary px-2 py-2 font-monospace";
                turretNavBadge.innerHTML = `<i class="fa-solid fa-microchip me-1"></i> TURRET: SIM`;
            }
        }

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

        // Locate Person target badge & status
        const activeTargetBadge = document.getElementById("activeTargetBadge");
        const locateStatusText = document.getElementById("locateStatusText");
        if (activeTargetBadge && locateStatusText) {
            if (data.locate_target) {
                activeTargetBadge.className = "badge bg-warning text-dark small font-monospace fw-bold";
                activeTargetBadge.innerText = `TARGET: ${data.locate_target.toUpperCase()}`;
                locateStatusText.innerHTML = `<span class="text-warning"><i class="fa-solid fa-spinner fa-spin me-1"></i> Active Target: ${data.locate_target}</span>`;
            } else {
                activeTargetBadge.className = "badge bg-dark border border-warning text-warning small font-monospace";
                activeTargetBadge.innerText = "TARGET: NONE";
                locateStatusText.innerHTML = `<span class="text-secondary"><i class="fa-solid fa-circle-info me-1"></i> Status: Standby / No target set</span>`;
            }
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

        // Camera Flip button
        const flipText = document.getElementById("flipBtnText");
        const flipBtn = document.getElementById("toggleFlipBtn");
        if (flipText && flipBtn) {
            if (data.camera_flipped) {
                flipText.innerText = "Flip: ON";
                flipBtn.className = "btn btn-sm btn-light";
            } else {
                flipText.innerText = "Flip: OFF";
                flipBtn.className = "btn btn-sm btn-outline-light";
            }
        }
    } catch (err) {
        console.error("Status fetch error:", err);
    }
}

async function toggleCameraFlip() {
    try {
        const res = await fetch("/api/toggle_flip", { method: "POST" });
        const data = await res.json();
        const flipBtn = document.getElementById("toggleFlipBtn");
        const flipText = document.getElementById("flipBtnText");
        if (data.camera_flipped) {
            flipText.innerText = "Flip: ON";
            flipBtn.className = "btn btn-sm btn-light";
        } else {
            flipText.innerText = "Flip: OFF";
            flipBtn.className = "btn btn-sm btn-outline-light";
        }
    } catch (err) {
        console.error("Camera flip error:", err);
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

function updateSelectedFilesCount() {
    const fileInput = document.getElementById("uploadPhotoInput");
    const badge = document.getElementById("selectedFilesBadge");
    if (!fileInput || !badge) return;
    const count = fileInput.files ? fileInput.files.length : 0;
    badge.innerText = `${count} selected`;
    badge.className = count > 0 ? "badge bg-info text-dark font-monospace" : "badge bg-secondary font-monospace";
}

async function uploadUserPhotos() {
    const nameInput = document.getElementById("newUserName");
    const roleInput = document.getElementById("newUserRole");
    const fileInput = document.getElementById("uploadPhotoInput");
    const uploadBtn = document.getElementById("uploadPhotosBtn");
    const feedback = document.getElementById("uploadFeedback");
    const name = nameInput.value.trim();
    const role = roleInput.value.trim() || "Authorized Personnel";

    if (!name) {
        alert("Please enter the person's full name first.");
        nameInput.focus();
        return;
    }
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select one or more photo files to upload.");
        return;
    }

    const totalFiles = fileInput.files.length;
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin me-1"></i> Converting to Embeddings (${totalFiles} files)...`;
    if (feedback) {
        feedback.className = "small mb-2 text-info";
        feedback.innerText = "Extracting facial features and indexing vectors into ChromaDB...";
        feedback.classList.remove("d-none");
    }

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
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-up me-1"></i> Upload & Convert to Embeddings (ChromaDB)`;
            return;
        }
        activeEnrollmentUserId = createData.user.id;
    }

    // 2. Prepare FormData with all selected files
    const formData = new FormData();
    formData.append("user_id", activeEnrollmentUserId);
    formData.append("name", name);
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append("photos", fileInput.files[i]);
    }

    try {
        const res = await fetch("/api/upload_photos", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            uploadBtn.className = "btn btn-sm btn-success w-100";
            uploadBtn.innerHTML = `<i class="fa-solid fa-circle-check me-1"></i> Indexed ${data.processed_count} vectors into ChromaDB!`;
            if (feedback) {
                feedback.className = "small mb-2 text-success";
                feedback.innerText = data.message;
            }
            loadUsers();
            fetchStatus();
        } else {
            alert(data.error || "Failed to process photos.");
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-up me-1"></i> Upload & Convert to Embeddings (ChromaDB)`;
            if (feedback) {
                feedback.className = "small mb-2 text-danger";
                feedback.innerText = data.error || "Processing failed.";
            }
        }
    } catch (err) {
        console.error("Upload error:", err);
        alert("Upload error: " + err);
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-up me-1"></i> Upload & Convert to Embeddings (ChromaDB)`;
    }
}
const uploadUserPhoto = uploadUserPhotos;

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

    const fileInput = document.getElementById("uploadPhotoInput");
    if (fileInput) fileInput.value = "";
    updateSelectedFilesCount();

    const uploadBtn = document.getElementById("uploadPhotosBtn");
    if (uploadBtn) {
        uploadBtn.className = "btn btn-sm btn-outline-info w-100";
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-up me-1"></i> Upload & Convert to Embeddings (ChromaDB)`;
    }
    const feedback = document.getElementById("uploadFeedback");
    if (feedback) {
        feedback.className = "small mb-2 text-info d-none";
        feedback.innerText = "";
    }

    const modal = bootstrap.Modal.getInstance(document.getElementById("addUserModal"));
    if (modal) modal.hide();
    loadUsers();
    fetchStatus();
}

async function submitLocatePerson() {
    const input = document.getElementById("locateInput");
    const name = input ? input.value.trim() : "";
    if (!name) return;

    try {
        const res = await fetch("/api/command", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command: `locate ${name}` })
        });
        const data = await res.json();
        if (data.success) {
            fetchStatus();
        }
    } catch (e) {
        console.error("Error setting locate target:", e);
    }
}

async function clearLocatePerson() {
    try {
        const input = document.getElementById("locateInput");
        if (input) input.value = "";
        const res = await fetch("/api/command", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command: "stop locating" })
        });
        const data = await res.json();
        if (data.success) {
            fetchStatus();
        }
    } catch (e) {
        console.error("Error clearing locate target:", e);
    }
}

// ==========================================
// ESP32 TURRET & CALIBRATION CONTROLLER
// ==========================================

let activeTurretStatus = null;
let isUserDraggingSlider = false;

async function fetchTurretStatus() {
    try {
        const res = await fetch("/api/turret/status");
        if (!res.ok) return;
        const data = await res.json();
        const st = data.status || {};
        const calib = st.calibration || {};
        activeTurretStatus = st;

        // 1. Live angles display
        const panDisp = document.getElementById("livePanDisplay");
        const tiltDisp = document.getElementById("liveTiltDisplay");
        if (panDisp) panDisp.innerText = `${st.pan.toFixed(1)}°`;
        if (tiltDisp) tiltDisp.innerText = `${st.tilt.toFixed(1)}°`;

        // 2. Hardware connection status badge
        const connBadge = document.getElementById("turretConnBadge");
        if (connBadge) {
            if (st.connected) {
                connBadge.className = "badge bg-success-subtle text-success border border-success small font-monospace";
                connBadge.innerText = `CONNECTED (${st.port})`;
            } else if (st.is_mock) {
                connBadge.className = "badge bg-dark border border-secondary text-secondary small font-monospace";
                connBadge.innerText = "SIMULATION (No HW)";
            } else {
                connBadge.className = "badge bg-danger-subtle text-danger border border-danger small font-monospace";
                connBadge.innerText = "DISCONNECTED";
            }
        }

        // 3. Tab Laser state
        const tabLaserState = document.getElementById("turretLaserState");
        if (tabLaserState) {
            tabLaserState.innerText = st.laser ? "ON" : "OFF";
            tabLaserState.className = st.laser ? "text-danger fw-bold fa-beat" : "text-secondary";
        }

        // 4. Laser toggle button
        const btnToggleLaser = document.getElementById("btnToggleLaser");
        const laserBtnText = document.getElementById("laserBtnText");
        if (btnToggleLaser && laserBtnText) {
            if (st.laser) {
                laserBtnText.innerText = "Laser: ON (FIRING)";
                btnToggleLaser.className = "btn btn-sm btn-danger flex-fill fa-beat";
            } else {
                laserBtnText.innerText = "Laser: OFF";
                btnToggleLaser.className = "btn btn-sm btn-outline-danger flex-fill";
            }
        }

        // 5. Populate COM ports dropdown if needed
        const portSelect = document.getElementById("portSelect");
        if (portSelect && portSelect.options.length <= 1 && data.available_ports) {
            data.available_ports.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.device;
                opt.innerText = `${p.device} (${p.description || "Serial"})`;
                if (p.device === st.port) opt.selected = true;
                portSelect.appendChild(opt);
            });
        }

        // 6. Update calibration UI (only if user is not actively adjusting sliders)
        if (!isUserDraggingSlider) {
            const checkPan = document.getElementById("checkInvertPan");
            const checkTilt = document.getElementById("checkInvertTilt");
            const panFov = document.getElementById("panFovSlider");
            const tiltFov = document.getElementById("tiltFovSlider");
            const smoothing = document.getElementById("smoothingSlider");

            if (checkPan) checkPan.checked = !!calib.pan_inverted;
            if (checkTilt) checkTilt.checked = !!calib.tilt_inverted;
            if (panFov && calib.pan_fov) {
                panFov.value = calib.pan_fov;
                document.getElementById("panFovVal").innerText = calib.pan_fov;
            }
            if (tiltFov && calib.tilt_fov) {
                tiltFov.value = calib.tilt_fov;
                document.getElementById("tiltFovVal").innerText = calib.tilt_fov;
            }
            if (smoothing && calib.smoothing) {
                smoothing.value = Math.round(calib.smoothing * 100);
                document.getElementById("smoothVal").innerText = calib.smoothing.toFixed(2);
            }
        }

    } catch (err) {
        console.error("Error fetching turret status:", err);
    }
}

async function setTurretMode(mode) {
    try {
        await fetch("/api/turret/set_mode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: mode })
        });
        fetchTurretStatus();
    } catch (e) {
        console.error("Error setting turret mode:", e);
    }
}

let panTimeout = null;
function onManualPanChange(val) {
    document.getElementById("manualPanVal").innerText = `${val}°`;
    const tilt = parseFloat(document.getElementById("manualTiltSlider").value) || 90;
    
    // Debounce slider updates to 30ms to prevent request flood
    clearTimeout(panTimeout);
    panTimeout = setTimeout(async () => {
        try {
            await fetch("/api/turret/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pan: parseFloat(val), tilt: tilt })
            });
            fetchTurretStatus();
        } catch (e) {
            console.error("Error moving pan:", e);
        }
    }, 30);
}

let tiltTimeout = null;
function onManualTiltChange(val) {
    document.getElementById("manualTiltVal").innerText = `${val}°`;
    const pan = parseFloat(document.getElementById("manualPanSlider").value) || 90;

    clearTimeout(tiltTimeout);
    tiltTimeout = setTimeout(async () => {
        try {
            await fetch("/api/turret/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pan: pan, tilt: parseFloat(val) })
            });
            fetchTurretStatus();
        } catch (e) {
            console.error("Error moving tilt:", e);
        }
    }, 30);
}

async function toggleTurretLaser() {
    const currentState = activeTurretStatus ? activeTurretStatus.laser : false;
    try {
        await fetch("/api/turret/laser", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ laser: !currentState })
        });
        fetchTurretStatus();
    } catch (e) {
        console.error("Error toggling laser:", e);
    }
}

async function pulseTurretLaser() {
    try {
        await fetch("/api/turret/pulse", { method: "POST" });
        fetchTurretStatus();
    } catch (e) {
        console.error("Error pulsing laser:", e);
    }
}

async function centerTurretServos() {
    document.getElementById("manualPanSlider").value = 90;
    document.getElementById("manualTiltSlider").value = 90;
    document.getElementById("manualPanVal").innerText = "90°";
    document.getElementById("manualTiltVal").innerText = "90°";
    try {
        await fetch("/api/turret/move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pan: 90.0, tilt: 90.0, laser: false })
        });
        fetchTurretStatus();
    } catch (e) {
        console.error("Error centering turret:", e);
    }
}

async function calibrateCenterPosition() {
    try {
        const res = await fetch("/api/turret/calibrate_center", { method: "POST" });
        const data = await res.json();
        if (data.success) {
            alert(`[Calibration Saved] Center locked at Pan ${data.pan_center}° / Tilt ${data.tilt_center}°. Intruders will be targeted relative to this reference!`);
            fetchTurretStatus();
        }
    } catch (e) {
        alert("Failed to calibrate center: " + e.message);
    }
}

async function updateCalibrationSettings() {
    const invertPan = document.getElementById("checkInvertPan").checked;
    const invertTilt = document.getElementById("checkInvertTilt").checked;
    const panFov = parseFloat(document.getElementById("panFovSlider").value);
    const tiltFov = parseFloat(document.getElementById("tiltFovSlider").value);
    const smooth = parseFloat(document.getElementById("smoothingSlider").value) / 100.0;

    document.getElementById("panFovVal").innerText = panFov;
    document.getElementById("tiltFovVal").innerText = tiltFov;
    document.getElementById("smoothVal").innerText = smooth.toFixed(2);

    try {
        await fetch("/api/turret/calibrate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                pan_inverted: invertPan,
                tilt_inverted: invertTilt,
                pan_fov: panFov,
                tilt_fov: tiltFov,
                smoothing: smooth
            })
        });
        fetchTurretStatus();
    } catch (e) {
        console.error("Error updating calibration:", e);
    }
}

async function resetTurretCalibration() {
    if (!confirm("Reset all turret servo calibration settings to factory defaults (90° center, 60°/45° FOV)?")) {
        return;
    }
    try {
        await fetch("/api/turret/reset_calibration", { method: "POST" });
        fetchTurretStatus();
    } catch (e) {
        console.error("Error resetting calibration:", e);
    }
}

async function reconnectTurretPort() {
    const port = document.getElementById("portSelect").value;
    try {
        const res = await fetch("/api/turret/reconnect", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ port: port })
        });
        const data = await res.json();
        if (data.connected) {
            alert(`Connected successfully to ESP32 on ${data.port}!`);
        } else {
            alert(`Could not connect on ${port}. Operating in virtual simulation mode.`);
        }
        fetchTurretStatus();
    } catch (e) {
        console.error("Error reconnecting port:", e);
    }
}

// Interactive Click-to-Aim on Video Feed
async function onVideoFeedClick(event) {
    const img = event.target;
    const rect = img.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const clickY = event.clientY - rect.top;

    // Scale to native video resolution (640x480 standard)
    const nativeWidth = 640;
    const nativeHeight = 480;
    const scaleX = nativeWidth / rect.width;
    const scaleY = nativeHeight / rect.height;

    const frameX = clickX * scaleX;
    const frameY = clickY * scaleY;

    try {
        await fetch("/api/turret/aim_pixel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ x: frameX, y: frameY, laser: true })
        });
        fetchTurretStatus();
    } catch (e) {
        console.error("Error aiming at pixel:", e);
    }
}

