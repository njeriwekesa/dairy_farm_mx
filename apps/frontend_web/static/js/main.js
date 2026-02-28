document.addEventListener("DOMContentLoaded", function () {
    console.log("JS LOADED");

    // -----------------------------
    //  Config & State
    // -----------------------------
    const API_BASE = "/api";
    let currentFarmId = null;
    let cattleMap = {};         // id -> tag_number, used for milk display
    let allMilkRecords = [];    // full milk list for client-side grouping
    let currentTab = "daily";   // active summary tab

    // -----------------------------
    //  Auth helpers
    // -----------------------------
    function getToken() {
        return localStorage.getItem("access");
    }

    function authHeaders() {
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + getToken()
        };
    }

    function logout() {
        localStorage.clear();
        window.location.href = "/login/";
    }

    function renderNavbar() {
        const nav = document.getElementById("navbar");
        if (!nav) return;
        if (getToken()) {
            nav.innerHTML = `
                <a href="/dashboard/">Dashboard</a>
                <button onclick="logout()">Logout</button>
            `;
        } else {
            nav.innerHTML = `
                <a href="/login/">Login</a>
                <a href="/register/">Register</a>
            `;
        }
    }

    renderNavbar();

    // -----------------------------
    //  Register
    // -----------------------------
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("reg_email").value;
            const username = document.getElementById("reg_username").value;
            const password = document.getElementById("reg_password").value;
            const farm_name = document.getElementById("reg_farm_name").value;

            const registerRes = await fetch(`${API_BASE}/users/register/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, username, password, farm_name })
            });

            const registerData = await registerRes.json();

            if (!registerRes.ok) {
                const errors = Object.entries(registerData)
                    .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`)
                    .join("\n");
                document.getElementById("registerMessage").innerText = errors;
                return;
            }

            // Auto-login after register
            const loginRes = await fetch(`${API_BASE}/token/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const loginData = await loginRes.json();
            if (loginRes.ok) {
                localStorage.setItem("access", loginData.access);
                window.location.href = "/dashboard/";
            } else {
                document.getElementById("registerMessage").innerText =
                    "Registration succeeded but auto-login failed.";
            }
        });
    }

    // -----------------------------
    //  Login
    // -----------------------------
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login_email").value;
            const password = document.getElementById("login_password").value;

            const res = await fetch(`${API_BASE}/token/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (res.ok) {
                localStorage.setItem("access", data.access);
                window.location.href = "/dashboard/";
            } else {
                document.getElementById("loginMessage").innerText = "Invalid login.";
            }
        });
    }

    // -----------------------------
    //  Farm
    // -----------------------------
    async function loadFarm() {
        const res = await fetch(`${API_BASE}/farms/`, { headers: authHeaders() });
        if (!res.ok) { console.error("Failed to load farm:", res.status); return; }
        const farms = await res.json();
        if (farms.length > 0) {
            currentFarmId = farms[0].id;
            console.log("Farm loaded, ID:", currentFarmId);
        } else {
            console.warn("No farms found for this user.");
        }
    }

    // -----------------------------
    //  Cattle CRUD
    // -----------------------------
    async function loadCattle(filterTag = "") {
        const res = await fetch(`${API_BASE}/cattle/`, { headers: authHeaders() });
        if (!res.ok) { console.error("Failed to load cattle:", res.status); return; }
        const cattle = await res.json();

        const tbody = document.getElementById("cattleList");
        const dropdown = document.getElementById("milkCattle");
        if (!tbody) return;

        // Rebuild lookup map
        cattleMap = {};
        cattle.forEach(c => { cattleMap[c.id] = c.tag_number; });

        tbody.innerHTML = "";
        if (dropdown) dropdown.innerHTML = `<option value="">Select Cattle</option>`;

        cattle
            .filter(c => c.tag_number.toLowerCase().includes(filterTag.toLowerCase()))
            .forEach(c => {
                tbody.innerHTML += `
                    <tr>
                        <td>${c.tag_number}</td>
                        <td>${c.breed}</td>
                        <td>${c.gender}</td>
                        <td>
                            <button onclick="editCattle(${c.id}, '${c.tag_number}', '${c.breed}', '${c.gender}')">Edit</button>
                            <button onclick="deleteCattle(${c.id})">Delete</button>
                        </td>
                    </tr>
                `;
                if (dropdown) {
                    dropdown.innerHTML += `<option value="${c.id}">${c.tag_number}</option>`;
                }
            });
    }

    function editCattle(id, tag, breed, gender) {
        document.getElementById("editCattleId").value = id;
        document.getElementById("cattleTag").value = tag;
        document.getElementById("cattleBreed").value = breed;
        document.getElementById("cattleGender").value = gender;
        document.getElementById("cattleFormTitle").innerText = "Edit Cattle";
        document.getElementById("cattleSubmitBtn").innerText = "Save Changes";
        document.getElementById("cattleCancelBtn").style.display = "inline";
        // Tag is immutable per unique_together constraint — disable it during edit
        document.getElementById("cattleTag").disabled = true;
    }

    function cancelCattleEdit() {
        document.getElementById("editCattleId").value = "";
        document.getElementById("cattleTag").value = "";
        document.getElementById("cattleTag").disabled = false;
        document.getElementById("cattleBreed").value = "";
        document.getElementById("cattleGender").value = "";
        document.getElementById("cattleFormTitle").innerText = "Add Cattle";
        document.getElementById("cattleSubmitBtn").innerText = "Add Cattle";
        document.getElementById("cattleCancelBtn").style.display = "none";
    }

    async function submitCattle() {
        const editId = document.getElementById("editCattleId").value;
        const tag = document.getElementById("cattleTag").value.trim();
        const breed = document.getElementById("cattleBreed").value.trim();
        const gender = document.getElementById("cattleGender").value;

        if (!breed || !gender) {
            alert("Please fill in Breed and Gender.");
            return;
        }

        if (editId) {
            // PATCH existing cattle — farm and tag_number are read-only on update
            const res = await fetch(`${API_BASE}/cattle/${editId}/`, {
                method: "PATCH",
                headers: authHeaders(),
                body: JSON.stringify({ breed, gender })
            });
            if (!res.ok) {
                const err = await res.json();
                alert("Error: " + JSON.stringify(err));
                return;
            }
        } else {
            // POST new cattle
            if (!tag) { alert("Please fill in Tag Number."); return; }
            if (!currentFarmId) { alert("Farm not loaded. Please refresh."); return; }
            const res = await fetch(`${API_BASE}/cattle/`, {
                method: "POST",
                headers: authHeaders(),
                body: JSON.stringify({ tag_number: tag, breed, gender, farm: currentFarmId })
            });
            if (!res.ok) {
                const err = await res.json();
                alert("Error: " + JSON.stringify(err));
                return;
            }
        }

        cancelCattleEdit();
        loadCattle();
    }

    async function deleteCattle(id) {
        if (!confirm("Delete this cattle record?")) return;
        await fetch(`${API_BASE}/cattle/${id}/`, { method: "DELETE", headers: authHeaders() });
        loadCattle();
        loadMilk();
    }

    document.getElementById("searchCattleBtn")?.addEventListener("click", () => {
        loadCattle(document.getElementById("searchCattleTag").value);
    });

    document.getElementById("clearCattleSearchBtn")?.addEventListener("click", () => {
        document.getElementById("searchCattleTag").value = "";
        loadCattle();
    });

    // -----------------------------
    //  Milk CRUD
    // -----------------------------
    async function loadMilk(tagFilter = "", startDate = "", endDate = "") {
        let url = `${API_BASE}/milk/`;
        const params = [];
        if (tagFilter) params.push(`cattle__tag_number=${encodeURIComponent(tagFilter)}`);
        if (startDate) params.push(`start_date=${startDate}T00:00:00`);
        if (endDate)   params.push(`end_date=${endDate}T23:59:59`);
        if (params.length) url += `?${params.join("&")}`;

        const res = await fetch(url, { headers: authHeaders() });
        if (!res.ok) { console.error("Failed to load milk:", res.status); return; }

        allMilkRecords = await res.json();
        renderMilkTable(allMilkRecords);
        renderSummaryTab(currentTab);
    }

    function renderMilkTable(records) {
        const tbody = document.getElementById("milkList");
        if (!tbody) return;

        tbody.innerHTML = "";
        let total = 0;

        records.forEach(m => {
            total += parseFloat(m.liters);
            const dateStr = m.date_time ? m.date_time.replace("T", " ").substring(0, 16) : "";
            const tag = cattleMap[m.cattle] || m.cattle;
            tbody.innerHTML += `
                <tr>
                    <td>${tag}</td>
                    <td>${m.liters}</td>
                    <td>${dateStr}</td>
                    <td>
                        <button onclick="editMilk(${m.id}, ${m.cattle}, ${m.liters}, '${m.date_time}')">Edit</button>
                        <button onclick="deleteMilk(${m.id})">Delete</button>
                    </td>
                </tr>
            `;
        });

        document.getElementById("totalMilk").innerText = total.toFixed(2);
    }

    function editMilk(id, cattleId, liters, dateTime) {
        document.getElementById("editMilkId").value = id;
        document.getElementById("milkCattle").value = cattleId;
        document.getElementById("milkCattle").disabled = true; // cattle is read-only on update
        document.getElementById("milkLiters").value = liters;
        // Convert "2026-02-27T10:00:00Z" -> "2026-02-27T10:00" for datetime-local input
        document.getElementById("milkDate").value = dateTime.substring(0, 16);
        document.getElementById("milkFormTitle").innerText = "Edit Record";
        document.getElementById("milkSubmitBtn").innerText = "Save Changes";
        document.getElementById("milkCancelBtn").style.display = "inline";
    }

    function cancelMilkEdit() {
        document.getElementById("editMilkId").value = "";
        document.getElementById("milkCattle").value = "";
        document.getElementById("milkCattle").disabled = false;
        document.getElementById("milkLiters").value = "";
        document.getElementById("milkDate").value = "";
        document.getElementById("milkFormTitle").innerText = "Add Record";
        document.getElementById("milkSubmitBtn").innerText = "Add Record";
        document.getElementById("milkCancelBtn").style.display = "none";
    }

    async function submitMilk() {
        const editId = document.getElementById("editMilkId").value;
        const liters = document.getElementById("milkLiters").value;
        const cattle = document.getElementById("milkCattle").value;
        const date_time = document.getElementById("milkDate").value;

        if (!liters || !cattle || !date_time) {
            alert("Please select cattle, enter liters, and pick a date/time.");
            return;
        }

        if (editId) {
            // PATCH — cattle is read-only so only send liters and date_time
            const res = await fetch(`${API_BASE}/milk/${editId}/`, {
                method: "PATCH",
                headers: authHeaders(),
                body: JSON.stringify({ liters, date_time })
            });
            if (!res.ok) {
                const err = await res.json();
                alert("Error: " + JSON.stringify(err));
                return;
            }
        } else {
            const res = await fetch(`${API_BASE}/milk/`, {
                method: "POST",
                headers: authHeaders(),
                body: JSON.stringify({ liters, cattle, date_time })
            });
            if (!res.ok) {
                const err = await res.json();
                alert("Error: " + JSON.stringify(err));
                return;
            }
        }

        cancelMilkEdit();
        loadMilk();
    }

    async function deleteMilk(id) {
        if (!confirm("Delete this milk record?")) return;
        await fetch(`${API_BASE}/milk/${id}/`, { method: "DELETE", headers: authHeaders() });
        loadMilk();
    }

    document.getElementById("searchMilkBtn")?.addEventListener("click", () => {
        const tag   = document.getElementById("searchMilkTag").value.trim();
        const start = document.getElementById("searchMilkStart").value;
        const end   = document.getElementById("searchMilkEnd").value;
        loadMilk(tag, start, end);
    });

    document.getElementById("clearMilkSearchBtn")?.addEventListener("click", () => {
        document.getElementById("searchMilkTag").value = "";
        document.getElementById("searchMilkStart").value = "";
        document.getElementById("searchMilkEnd").value = "";
        loadMilk();
    });

    // -----------------------------
    //  Milk Summary Tabs
    // -----------------------------
    function switchTab(period) {
        currentTab = period;
        // Highlight active tab
        ["daily", "weekly", "monthly"].forEach(p => {
            const btn = document.getElementById("tab" + p.charAt(0).toUpperCase() + p.slice(1));
            if (btn) btn.style.fontWeight = p === period ? "bold" : "normal";
        });
        renderSummaryTab(period);
    }

    function renderSummaryTab(period) {
        const tbody = document.getElementById("summaryList");
        const header = document.getElementById("summaryPeriodHeader");
        const empty = document.getElementById("summaryEmpty");
        if (!tbody) return;

        // Group allMilkRecords by the chosen period
        const groups = {};
        allMilkRecords.forEach(m => {
            const d = new Date(m.date_time);
            let key;
            if (period === "daily") {
                key = d.toISOString().substring(0, 10); // YYYY-MM-DD
            } else if (period === "weekly") {
                // ISO week: get Monday of that week
                const day = d.getDay() || 7; // Sun=7
                const monday = new Date(d);
                monday.setDate(d.getDate() - day + 1);
                key = "Week of " + monday.toISOString().substring(0, 10);
            } else {
                key = d.toISOString().substring(0, 7); // YYYY-MM
            }
            groups[key] = (groups[key] || 0) + parseFloat(m.liters);
        });

        const keys = Object.keys(groups).sort().reverse();

        if (header) {
            header.innerText = period === "daily" ? "Date" : period === "weekly" ? "Week" : "Month";
        }

        if (keys.length === 0) {
            tbody.innerHTML = "";
            if (empty) empty.style.display = "block";
            return;
        }

        if (empty) empty.style.display = "none";
        tbody.innerHTML = keys.map(k => `
            <tr>
                <td>${k}</td>
                <td>${groups[k].toFixed(2)} L</td>
            </tr>
        `).join("");
    }

    // Set initial active tab style
    switchTab("daily");

    // Make summary tab switching global for onclick
    window.switchTab = switchTab;

    // -----------------------------
    //  Auto-load on dashboard
    // -----------------------------
    if (window.location.pathname === "/dashboard/") {
        loadFarm().then(() => {
            loadCattle();
            loadMilk();
        });
    }

    // Expose functions used by inline onclick handlers
    window.submitCattle = submitCattle;
    window.editCattle = editCattle;
    window.cancelCattleEdit = cancelCattleEdit;
    window.deleteCattle = deleteCattle;
    window.submitMilk = submitMilk;
    window.editMilk = editMilk;
    window.cancelMilkEdit = cancelMilkEdit;
    window.deleteMilk = deleteMilk;
    window.logout = logout;
});