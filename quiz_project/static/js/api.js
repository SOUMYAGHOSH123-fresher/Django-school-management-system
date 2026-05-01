  // ================= TOKEN HELPERS =================
    function getAccess() {
        return localStorage.getItem("access");
    }

    function getRefresh() {
        return localStorage.getItem("refresh");
    }

    function setTokens(access, refresh = null) {
        localStorage.setItem("access", access);
        if (refresh) localStorage.setItem("refresh", refresh);
    }

    function logout() {
        localStorage.clear();
        window.location.href = "/dashboard/";
    }

    async function refreshToken() {
        try {
            apiFetch(`${BASE_URL}/refresh-token/`, {
                method: "POST"
            })
                .then(res => res.json())
                .then(data => {
                    if (data.access) {
                        setTokens(data.access);
                        return data.access;
                    } else {
                        logout();
                    }
                });

        } catch (error) {
            logout();
        }
    }

    async function apiFetch(url, options = {}, retry = true) {
        let access = getAccess();

        options.headers = {
            ...(options.headers || {}),
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access
        };

        let response = await fetch(url, options);

        // 🔥 If token expired
        if (response.status === 401 && retry) {
            const newAccess = await refreshToken();

            if (!newAccess) return;

            options.headers["Authorization"] = "Bearer " + newAccess;

            // retry request with new token
            return apiFetch(url, options, false);
        }

        return response;
    }

    const token = localStorage.getItem("access");

    // ================= AUTH GUARD =================
    if (!token) {
        window.location.href = "/dashboard/";
    }

    // Decode JWT (simple)
    function parseJwt(token) {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch {
            return null;
        }
    }

    const user = parseJwt(token);
    const role = user?.role;

    if (!user || !user.role) {
        localStorage.clear();
        window.location.href = "/dashboard/";
    }

    document.getElementById("userRole").innerText = user.role;


    // ========   SetPage ===========
    function setPage(title, fn) {
        document.getElementById("pageTitle").innerText = title;
        fn();
    }

    // ================= API HELPER =================
    function authHeaders() {
        return {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        };
    }



    