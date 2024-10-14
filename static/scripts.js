document.getElementById('voteForm').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const animal = formData.get('animal');

    fetch('/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ animal })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        document.getElementById('resultMessage').innerText = data.message;
        document.getElementById('voteForm').reset(); // Reset form
    })
    .catch(error => {
        document.getElementById('resultMessage').innerText = 'Error: ' + error.message;
    });
});

