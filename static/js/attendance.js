const container = document.getElementById('students-container');
document.getElementById('view-attendance').addEventListener('click', function () {
    const date = document.getElementById('attendance-date').value;
    const class_name = document.getElementById('class-select').value;
    const subject = document.getElementById('subject-select').value;
    if (date && class_name && subject) {
        fetch(`/attendance?date=${date}&class_name=${class_name}&subject=${subject}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    container.innerHTML = '';
                    data.data.forEach(student => {
                        const studentDiv = document.createElement('div');
                        studentDiv.id = `student-${student.id}`;
                        studentDiv.className = student.present ? 'student-div present' : 'student-div absent';
                        studentDiv.innerText = `${student.roll_no} - ${student.name}`;
                        container.appendChild(studentDiv);
                    });
                } else {
                    container.innerHTML = '';
                    showFlashMessage(data.message, 'error');
                }

            }).catch(error => {
                container.innerHTML = '';
                showFlashMessage('An error occurred while viewing attendance', 'error');
                console.error('Error:', error);
            });
    } else {
        showFlashMessage('Please select a date, subject and class.', 'error');
    }
});

document.getElementById('x').addEventListener('change', function () {
    const class_name = document.getElementById('class-select').value;
    if (class_name) {
        fetch(`/api/attendance/students?class_name=${class_name}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    container.innerHTML = '';
                    data.data.forEach(student => {
                        const studentDiv = document.createElement('div');
                        studentDiv.id = `student-${student.id}`;
                        studentDiv.className = 'student-div absent';
                        studentDiv.innerText = `${student.roll_no} - ${student.name}`;
                        studentDiv.addEventListener('click', function () {
                            this.classList.toggle('present');
                            this.classList.toggle('absent');
                        });
                        container.appendChild(studentDiv);
                    });
                } else {
                    container.innerHTML = '';
                    showFlashMessage(data.message, 'error');
                }

            }).catch(error => {
                showFlashMessage('An error occurred while fetching students', 'error');
                console.error('Error:', error);
            });
    }
});

document.getElementById('submit-attendance').addEventListener('click', function () {
    const class_name = document.getElementById('class-select').value;
    const subject = document.getElementById('subject-select').value;
    let attendance = [];
    document.querySelectorAll('.student-div.present').forEach((div) => {
        attendance.push({
            student_id: parseInt(div.id.split('-')[1]),
            present: true,
        });
    });
    document.querySelectorAll('.student-div.absent').forEach((div) => {
        attendance.push({
            student_id: parseInt(div.id.split('-')[1]),
            present: false,
        });
    });
    fetch('/api/attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'attendance': attendance, 'class_name': class_name, 'subject': subject }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                container.innerHTML = '';
                showFlashMessage('Attendance submitted successfully', 'success');
            } else {
                container.innerHTML = '';
                showFlashMessage(data.message, 'error');
            }
        })
        .catch((error) => {
            showFlashMessage('An error occurred while submitting attendance', 'error');
            console.error('Error:', error);
        });
});

window.onload = function () {
    var today = new Date();
    var day = String(today.getDate()).padStart(2, '0');
    var month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    var year = today.getFullYear();
    var formattedDate = year + '-' + month + '-' + day;
    document.getElementById('attendance-date').value = formattedDate;
};
