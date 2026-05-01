function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");

    const colors = {
        success: "bg-green-600",
        error: "bg-red-600",
        info: "bg-blue-600"
    };

    const toast = document.createElement("div");
    toast.className = `
        ${colors[type]} text-white px-4 py-3 rounded-lg shadow-lg
        transform transition-all duration-300 opacity-0 translate-x-10
    `;
    toast.innerText = message;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove("opacity-0", "translate-x-10");
    }, 100);

    // Remove after 3 sec
    setTimeout(() => {
        toast.classList.add("opacity-0", "translate-x-10");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}