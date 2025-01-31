document.getElementById('fetch-low-attendance').addEventListener('click', function () {
    const class_name = document.getElementById('class-select').value;
    const subject = document.getElementById('subject-select').value;
    const year = document.getElementById('year-select').value;
    const month = document.getElementById('month-select').value;

    if (class_name && subject && year && month) {
        fetch(`/attendance/low-attendance?class_name=${class_name}&subject=${subject}&year=${year}&month=${month}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const tableBody = document.querySelector('#low-attendance-table tbody');
                    tableBody.innerHTML = '';
                    data.data.students.forEach(student => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${student.roll_no}</td>
                            <td>${student.name}</td>
                            <td>${student.attendance_percentage.toFixed(2)}%</td>
                        `;
                        tableBody.appendChild(row);
                        });
                        showFlashMessage('Low attendance data fetched successfully.', 'success');
                    
                } else {
                    showFlashMessage(data.message, 'error');
                }



            })
            .catch(error => {
                console.error('Error fetching low attendance data:', error);
            });
    } else {
        showFlashMessage('Please select class, subject, year, and month.', 'error');
    }
});

document.getElementById('populate-dummy-data').addEventListener('click', function () {
    const class_name = document.getElementById('dummy-class-select').value;
    const subject = document.getElementById('dummy-subject-select').value;
    const days = document.getElementById('days-input').value;

    if (class_name && subject && days) {
        const formData = new FormData();
        formData.append('class_name', class_name);
        formData.append('subject', subject);
        formData.append('days', days);

        fetch('/attendance/populate-dummy', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showFlashMessage('Dummy data populated successfully.', 'success');
                } else {
                    showFlashMessage(data.message, 'error');
                }
            })
            .catch(error => {
                showFlashMessage('An error occurred while populating dummy data.', 'error');
                console.error('Error populating dummy data:', error);
            });
    } else {
        showFlashMessage('Please fill out all fields.', 'error');
    }
});
function date() {
    var today = new Date();
    var day = String(today.getDate()).padStart(2, '0');
    var month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    var year = today.getFullYear();
    var formattedDate = year + '-' + month + '-' + day;
    return [year, month, day];
}
var date = date();
document.getElementById('year-select').value = date[0];
document.getElementById('month-select').value = date[1];
