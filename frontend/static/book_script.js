const urlParams = new URLSearchParams(window.location.search);
const serverId = urlParams.get('server_id');
const apiBaseUrl = 'http://10.223.44.216:5000'; // 确保这里是Flask应用的地址

// 更新标题显示服务器名称
document.getElementById('serverId').textContent = serverId;

async function reserve() {
    const startTimeInput = document.getElementById('appointmentTimeStart');
    const endTimeInput = document.getElementById('appointmentTimeEnd');
    const nameInput = document.getElementById('name');

    const startTime = startTimeInput.value;
    const endTime = endTimeInput.value;
    const name = nameInput.value;

    if (!startTime || !endTime || !name) {
        alert('Please fill in the complete reservation information');
        return;
    }

    if (new Date(startTime) >= new Date(endTime)) {
        alert('The start time of the appointment cannot be later than the end time of the appointment');
        return;
    }

    try {
        const response = await fetch(`${apiBaseUrl}/appointments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ start_time: startTime, end_time: endTime, name: name, server_id: serverId })
        });

        if (response.ok) {
            alert('successful appointment');
            // 清空输入框
            startTimeInput.value = '';
            endTimeInput.value = '';
            nameInput.value = '';
            loadAppointments(); // 重新加载预约列表
        } else if (response.status === 409) {
            alert('Reservation time conflict, please choose another time');
        } else {
            alert('Failed appointment');
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
}


async function loadAppointments() {
    const response = await fetch(`${apiBaseUrl}/appointments?server_id=${serverId}`);
    if (response.ok) {
        const appointments = await response.json();
        const tbody = document.querySelector(".appointments-table tbody");
        tbody.innerHTML = ''; // Clear existing entries

        if (appointments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3">No appointment yet</td></tr>';
        } else {
            appointments.forEach(appt => {
                // 解析为 UTC 时间
                const startTime = new Date(appt.start_time);
                const endTime = new Date(appt.end_time);

                // 获取本地时间字符串
                const localStartTime = startTime.toLocaleString(undefined, { timeZone: 'UTC' });
                const localEndTime = endTime.toLocaleString(undefined, { timeZone: 'UTC' });

                // 显示为本地时间
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${localStartTime} - ${localEndTime}</td>
                    <td>${appt.name}</td>
                    <td><button class="cancel-button" onclick="cancelAppointment(${appt.id})">Cancel Appointment</button></td>
                `;
            });
        }
    } else {
        console.error('Failed to load appointments:', response.statusText);
    }
}


async function cancelAppointment(id) {
    // Ask the user to confirm the cancellation
    if (confirm('Are you sure you want to cancel the reservation?')) { // Confirm dialog with the message
        const response = await fetch(`${apiBaseUrl}/appointments/${id}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            alert('Reservation cancelled'); // Notify user of successful cancellation
            loadAppointments(); // Reload the appointment list
        } else {
            alert('Cancellation failure'); // Inform the user if the cancellation fails
        }
    } else {
        // If user does not confirm, do nothing
        console.log('Cancellation aborted.');
    }
}


document.addEventListener('DOMContentLoaded', function() {
    loadAppointments(); // 页面加载时先显示已有的预约
});
