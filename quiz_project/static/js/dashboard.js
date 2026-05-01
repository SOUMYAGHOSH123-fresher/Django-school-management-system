
// ================= MENU =================
const menu = document.getElementById("menu");

function loadMenu() {
    if (role === "principal") {
        menu.innerHTML = `
                <li><button onclick="setPage('Dashboard', loadDashboard)">Dashboard</button></li>
                <li><button onclick="setPage('Profile', loadProfilePage)">Profile</button></li>
                <li><button onclick="setPage('Teachers', loadTeachers)">Teachers</button></li>
                <li><button onclick="setPage('Students', loadStudents)">Students</button></li>
                <li><button onclick="setPage('Quizzes', loadQuizzes)">Quizzes</button></li>
                <li>
                    <button onclick="setPage('Bulk Students', loadBulkUpload)">
                        Bulk Students
                    </button>
                </li>
                <li>
                    <button onclick="setPage('Bulk Teachers', loadBulkTeachers)">
                        Bulk Teachers
                    </button>
                </li>
            `;
    }

    if (role !== "principal") {
        window.location.href = "/dashboard/" + role + "/";
    }
}

loadMenu();

// ================= PRINCIPAL =================
let quizChart, classChart, attemptChart;
function loadDashboard() {
    apiFetch(`${BASE_URL}/dashboard/principal/`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("content").innerHTML = `
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-white p-4 rounded shadow">Teachers: ${data.teachers}</div>
                    <div class="bg-white p-4 rounded shadow">Students: ${data.students}</div>
                    <div class="bg-white p-4 rounded shadow">Quizzes: ${data.quizzes}</div>
                    <div class="bg-white p-4 rounded shadow">Active: ${data.active_quizzes}</div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-2">
                    
                    <div class="bg-white p-6 rounded-xl shadow">
                        <h2 class="font-semibold mb-4">Quiz Status</h2>
                        <canvas id="quizStatusChart"></canvas>
                    </div>

                    <div class="bg-white p-6 rounded-xl shadow">
                        <h2 class="font-semibold mb-4">Students per Class</h2>
                        <canvas id="classChart"></canvas>
                    </div>

                    <div class="bg-white p-6 rounded-xl shadow md:col-span-2">
                        <h2 class="font-semibold mb-4">Quiz Attempts (Last 7 Days)</h2>
                        <canvas id="attemptChart"></canvas>
                    </div>

                </div>
                `;

            // Destroy old charts if they exist
            if (quizChart) quizChart.destroy();
            if (classChart) classChart.destroy();
            if (attemptChart) attemptChart.destroy();

            // Pie Chart
            quizChart = new Chart(document.getElementById('quizStatusChart'), {
                type: 'pie',
                data: {
                    labels: ['Active', 'Inactive'],
                    datasets: [{
                        data: [data.active_quizzes || 0, data.inactive_quizzes || 0],
                        backgroundColor: ['#22c55e', '#ef4444'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: ctx => `${ctx.label}: ${ctx.raw}`
                            }
                        }
                    },
                    animation: {
                        duration: 1000
                    }
                }
            });

            // Bar Chart
            classChart = new Chart(document.getElementById('classChart'), {
                type: 'bar',
                data: {
                    labels: data.class_labels || [],
                    datasets: [{
                        label: 'Students',
                        data: data.class_counts || [],
                        backgroundColor: '#3b82f6',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 800
                    }
                }
            });

            // Line Chart
            attemptChart = new Chart(document.getElementById('attemptChart'), {
                type: 'line',
                data: {
                    labels: data.attempt_labels || [],
                    datasets: [{
                        label: 'Attempts',
                        data: data.attempt_counts || [],
                        borderColor: '#f97316',
                        backgroundColor: 'rgba(249,115,22,0.2)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    },
                    animation: {
                        duration: 1000
                    }
                }
            });

        });
}

// ================= TEACHERS =================
function loadTeachers() {
    apiFetch(`${BASE_URL}/dashboard/principal/teachers/`)
        .then(res => res.json())
        .then(data => {
            let html = "<h2 class='text-xl mb-4'>Teachers</h2>";

            data.teachers.forEach(t => {
                html += `
                    <div class="bg-white p-3 mb-2 rounded shadow flex justify-between">
                        <span>${t.email}</span>
                        <span>
                            ${t.is_approved ?
                        `
                                <button onclick="reject(${t.id})" class="text-red-600 ml-2">Reject</button>
                            ` : `
                                <button onclick="approve(${t.id})" class="text-green-600">Approve</button>
                            `}
                        </span>
                    </div>
                `;
            });

            document.getElementById("content").innerHTML = html;
        });
}

function approve(id) {
    apiFetch(`${BASE_URL}/dashboard/principal/approve-user/${id}/`, {
        method: "POST"
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadTeachers();
            } else {
                alert(data.error || "Something went wrong");
            }
        });
}

function reject(id) {
    apiFetch(`${BASE_URL}/dashboard/principal/reject-user/${id}/`, {
        method: "POST"
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadTeachers();
            } else {
                alert(data.error || "Something went wrong");
            }
        });
}

// ================= STUDENTS =================
function loadStudents() {
    apiFetch(`${BASE_URL}/dashboard/principal/students/`)
        .then(res => res.json())
        .then(data => {
            let html = "<h2 class='text-xl mb-4'>Students</h2>";

            data.students.forEach(s => {
                html += `
                    <div class="bg-white p-3 mb-2 rounded shadow flex justify-between">
                        <span>${s.email}</span>
                        ${s.student_class ? s.student_class.class_name : "No Class"}
                        <span>
                            ${s.is_approved ? `
                                <button onclick="reject(${s.id})" class="text-red-600 ml-2">Reject</button>
                            ` : `
                                <button onclick="approve(${s.id})" class="text-green-600">Approve</button>
                            `}
                        </span>
                    </div>
                    `;
            });

            document.getElementById("content").innerHTML = html;
        });
}

// ================= QUIZZES =================
function loadQuizzes() {
    apiFetch(`${BASE_URL}/dashboard/principal/quizzes/`)
        .then(res => res.json())
        .then(data => {
            let html = "<h2 class='text-xl mb-4'>Quizzes</h2>";

            data.quizzes.forEach(q => {
                html += `
                        <div class="bg-white p-3 mb-2 rounded shadow flex justify-between" >
                            <span>${q.title}</span>
                            <span>
                                <button onclick="toggleQuiz(${q.id})" class="text-blue-600">Toggle</button>
                                <button onclick="deleteQuiz(${q.id})" class="text-red-600 ml-2">Delete</button>
                            </span>
                        </div >
                        `;
            });

            document.getElementById("content").innerHTML = html;
        });
}

function toggleQuiz(id) {
    fetch(`${BASE_URL}/dashboard/principal/toggle-quiz/${id}/`)
        .then(loadQuizzes);
}

function deleteQuiz(id) {
    fetch(`${BASE_URL}/dashboard/principal/delete-quiz/${id}/`)
        .then(loadQuizzes);
}

// ================= INIT =================

if (role === "principal") {
    loadDashboard();
}



