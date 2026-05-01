

// PRINCIPAL BULK STUDENT UPLOAD (EXCEL + SUBJECT MAPPING) -->

// ================= BULK STUDENT UI =================
function loadBulkUpload() {
    document.getElementById("content").innerHTML = `
            <div class="bg-white p-6 rounded shadow max-w-4xl">
                <h2 class="text-xl font-bold mb-4">Bulk Student Upload (Excel)</h2>

                <input type="file" id="excelFile" accept=".xlsx,.xls"
                    class="w-full border p-2 mb-4">

                <button onclick="handleExcelUpload()"
                    class="bg-blue-600 text-white px-4 py-2 rounded">
                    Upload Excel
                </button>

            <div id="preview" class="mt-6"></div>
            </div>
        `;
}

// ================= HANDLE FILE =================
function handleFileUpload() {
    const file = document.getElementById("fileInput").files[0];

    if (!file) {
        alert("Select a file first");
        return;
    }

    const reader = new FileReader();

    reader.onload = function (e) {
        try {
            const data = JSON.parse(e.target.result);

            if (!Array.isArray(data)) {
                alert("JSON must be array");
                return;
            }

            renderPreview(data);
            sendBulkStudents(data);

        } catch {
            alert("Invalid JSON file");
        }
    };

    reader.readAsText(file);
}


function handleExcelUpload() {
    const file = document.getElementById("excelFile").files[0];

    if (!file) {
        alert("Select Excel file");
        return;
    }

    const reader = new FileReader();

    reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: "array" });

        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(sheet);

        if (!jsonData.length) {
            alert("Empty file");
            return;
        }

        renderPreview(jsonData);
        sendBulkStudents(jsonData);
    };

    reader.readAsArrayBuffer(file);
}

// ================= PREVIEW =================
function renderPreview(data) {
    let html = `
            <h3 class="font-semibold mb-2">Preview (${data.length})</h3>
            <table class="w-full bg-white border">
                <thead class="bg-gray-200">
                    <tr>
                        <th class="p-2">Email</th>
                        <th class="p-2">Name</th>
                        <th class="p-2">Class</th>
                    </tr>
                </thead>
                <tbody>
        `;

    data.forEach(s => {
        html += `
        <tr class="border-t">
            <td class="p-2">${s.email}</td>
            <td class="p-2">${s.first_name} ${s.last_name}</td>
            <td class="p-2">${s.class_name}</td>
        </tr>
    `;
    });

    html += `</tbody></table>`;

    document.getElementById("preview").innerHTML = html;
}

// ================= API CALL =================
function sendBulkStudents(data) {
    apiFetch(`${BASE_URL}/dashboard/teacher/bulk-students/`, {
        method: "POST",
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(res => {
            alert(res.message || "Upload done");
        })
        .catch(() => alert("Upload failed"));
}

// ================= SAMPLE =================
function downloadSample() {
    const sample = [
        {
            "email": "student1@gmail.com",
            "password": "test123",
            "first_name": "John",
            "last_name": "Doe",
            "role": "student",
            "student_class": 1
        }
    ];

    const blob = new Blob([JSON.stringify(sample, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "students.json";
    a.click();
}

function downloadExcelSample() {
    const ws = XLSX.utils.json_to_sheet([
        {
            email: "student@gmail.com",
            password: "test123",
            first_name: "John",
            last_name: "Doe",
            class_name: "Class 10"
        }
    ]);

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Students");

    XLSX.writeFile(wb, "students_sample.xlsx");
}



// PRINCIPAL BULK TEACHER UPLOAD (EXCEL + SUBJECT MAPPING) -->

// ================= LOAD UI =================
function loadBulkTeachers() {
    document.getElementById("content").innerHTML = `
    <div class="bg-white p-6 rounded shadow max-w-4xl">
        <h2 class="text-xl font-bold mb-4">Bulk Teacher Upload (Excel)</h2>

        <input type="file" id="teacherExcel" accept=".xlsx,.xls"
            class="w-full border p-2 mb-4">

        <div class="flex gap-2">
            <button onclick="handleTeacherExcel()"
                class="bg-blue-600 text-white px-4 py-2 rounded">
                Upload
            </button>

            <button onclick="downloadTeacherSample()"
                class="bg-gray-600 text-white px-4 py-2 rounded">
                Sample Excel
            </button>
        </div>

        <div id="teacherPreview" class="mt-6"></div>
    </div>
`;
}

// ================= HANDLE FILE =================
function handleTeacherExcel() {
    const file = document.getElementById("teacherExcel").files[0];

    if (!file) {
        alert("Select Excel file");
        return;
    }

    const reader = new FileReader();

    reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: "array" });

        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(sheet);

        if (!jsonData.length) {
            alert("Empty file");
            return;
        }

        renderTeacherPreview(jsonData);
        sendTeachers(jsonData);
    };

    reader.readAsArrayBuffer(file);
}

// ================= PREVIEW =================
function renderTeacherPreview(data) {
    let html = `
    <h3 class="font-semibold mb-2">Preview (${data.length})</h3>
    <table class="w-full bg-white border">
        <thead class="bg-gray-200">
            <tr>
                <th class="p-2">Email</th>
                <th class="p-2">Name</th>
                <th class="p-2">Subject</th>
            </tr>
        </thead>
        <tbody>
`;

    data.forEach(t => {
        html += `
        <tr class="border-t">
            <td class="p-2">${t.email}</td>
            <td class="p-2">${t.first_name} ${t.last_name}</td>
            <td class="p-2">${t.subject}</td>
        </tr>
    `;
    });

    html += `</tbody></table>`;

    document.getElementById("teacherPreview").innerHTML = html;
}

// ================= SEND =================
function sendTeachers(data) {
    apiFetch(`${BASE_URL}/dashboard/principal/bulk-teachers/`, {
        method: "POST",
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(res => {
            alert(`Created: ${res.created?.length || 0}\nFailed: ${res.failed?.length || 0}`);
        })
        .catch(() => alert("Upload failed"));
}

// ================= SAMPLE =================
function downloadTeacherSample() {
    const ws = XLSX.utils.json_to_sheet([
        {
            email: "teacher@gmail.com",
            password: "test123",
            first_name: "John",
            last_name: "Doe",
            subject: "Math"
        }
    ]);

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Teachers");

    XLSX.writeFile(wb, "teachers_sample.xlsx");
}
