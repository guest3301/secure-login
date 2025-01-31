document.addEventListener('DOMContentLoaded', () => {
    const socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('attendance_marked', (data) => {
        const userId = data.user_id;
        const userElement = document.getElementById(`user-${userId}`);
        if (userElement) {
            userElement.classList.add('marked');
        }
    });

    document.querySelectorAll('.attendance-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const userId = checkbox.dataset.userId;
            fetch('/api/attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
            });
        });
    });
});
