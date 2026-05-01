function loadProfilePage() {
    document.getElementById("content").innerHTML = `
    <div class="bg-white p-6 rounded-xl shadow max-w-lg">
        <h2 class="text-xl font-semibold mb-4">My Profile</h2>

        <input id="phone" placeholder="Phone" class="w-full p-2 border mb-2">
        <input id="address" placeholder="Address" class="w-full p-2 border mb-2">
        <textarea id="bio" placeholder="Bio" class="w-full p-2 border mb-2"></textarea>

        <button onclick="updateProfile()" class="bg-blue-600 text-white px-4 py-2 rounded">
            Update Profile
        </button>

        <p id="profile_msg" class="mt-2 text-sm"></p>
    </div>
`;

    loadProfile();
}

function loadProfile() {
    apiFetch(`${BASE_URL}/dashboard/profile/`)
        .then(res => res.json())
        .then(data => {
            phone.value = data.phone || "";
            address.value = data.address || "";
            bio.value = data.bio || "";
        });
}

function updateProfile() {
    apiFetch(`${BASE_URL}/dashboard/profile/`, {
        method: "PUT",
        body: JSON.stringify({
            phone: phone.value,
            address: address.value,
            bio: bio.value
        })
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById("profile_msg").innerHTML =
                "<span class='text-green-600'>Profile updated</span>";
        });
}


loadProfile();