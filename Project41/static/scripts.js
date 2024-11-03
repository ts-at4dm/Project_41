$(document).ready(function() {
    fetchUsers();

    $('#add-button').on('click', async function() {
        await createUser();
    });

    $('#update-button').on('click', function() {
        const id = $('#user-id').val();
        if (id) {
            updateUser(id);
        } else {
            alert('Please enter the Employee ID to update.');
        }
    });
});

function validateEmployee(id) {
    return /^\d+$/.test(id); // Check if the ID contains only digits
}

function validateName(name) {
    return /^[A-Za-z]+$/.test(name); // Check if the name contains only letters
}


// ==============================================================

async function fetchUsers() {
    try {
        const response = await fetch('/users');
        if (!response.ok) {
            throw new Error(`Error fetching users: ${response.statusText}`);
        }
        const users = await response.json();
        const tbody = $('#user-table tbody');
        tbody.empty();
        users.forEach(user => {
            tbody.append(`<tr>
                <td>${user.employee_id}</td>
                <td>${user.first_name}</td>
                <td>${user.last_name}</td>
                <td>
                    <button onclick="deleteUser(${user.employee_id})">Delete</button>
                </td>
            </tr>`);
        });
    } catch (error) {
        console.error("Error fetching users:", error.message);
    }
}

// ==============================================================

async function createUser() {
    const newUser = {
        first_name: $('#fname').val(),
        last_name: $('#lname').val()
    };

    if(!validateName(newUser.first_name)) {
        alert('Please enter alphabetical characters Only')
        return
    }

    if(!validateName(newUser.last_name)) {
        alert('Please enter alphabetical characters Only')
        return
    }
    
    try {
        const response = await fetch('/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newUser)
        });
        if (!response.ok) {
            throw new Error(`Error creating user: ${response.statusText}`);
        }
        const data = await response.json();
        fetchUsers();
        $('#user-form')[0].reset();
        $('#user-id').val('');
    } catch (error) {
        console.error("Error creating user:");
        alert('Error creating user: ');
    }
}

// ==============================================================


// ==============================================================

async function updateUser(employee_id) {
    const updatedUser = {
        employee_id: $('#user-id').val(),
        first_name: $('#fname').val(),
        last_name: $('#lname').val()
    };

    if(!validateEmployee(updatedUser.employee_id)) {
        alert('Please enter numerical characters only')
        return;
    }

    if(!validateName(updatedUser.first_name)) {
        alert('Please enter alphabetical characters Only')
        return;
    }

    if(!validateName(updatedUser.last_name)) {
        alert('Please enter alphabetical characters Only')
        return;
    }

    try {
        const response = await fetch(`/users/${employee_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                employee_id: updatedUser.employee_id,
                first_name: updatedUser.first_name,
                last_name: updatedUser.last_name
            }) // Send only the first and last name for update
        });

        if (!response.ok) {
            throw new Error(`Error updating user: ${response.statusText}`);
        }
        
        if (response.status === 404) {
            alert('Entry does not exist');
            return; // Exit if user not found
        }

        fetchUsers();
        $('#user-form')[0].reset();
        $('#user-id').val('');
    } catch (error) {
        alert('Error updating user: Entry does not exist');
    }
}

// ==============================================================

async function deleteUser(employee_id) {
    if (confirm('Are you sure you want to delete this user?')) {
        try {
            const response = await fetch(`/users/${employee_id}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error(`Error deleting user: ${response.statusText}`);
            }
            const data = await response.json();
            fetchUsers();
            alert(data.message);
        } catch (error) {
            alert('Error deleting user: ' + error.message);
        }
    }
}
