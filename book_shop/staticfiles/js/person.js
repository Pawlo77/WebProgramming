function toggleLike(reviewId) {
    fetch(`/reviews/${reviewId}/like/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok.');
            }
        })
        .then(data => {
            document.getElementById(`like-count-${reviewId}`).innerText = data.like_count;
            document.getElementById(`dislike-count-${reviewId}`).innerText = data.dislike_count;

            document.getElementById(`dislike-active-${reviewId}`).style.display = "none";
            document.getElementById(`dislike-inactive-${reviewId}`).style.display = "";
            if (data.liked) {
                document.getElementById(`like-active-${reviewId}`).style.display = "";
                document.getElementById(`like-inactive-${reviewId}`).style.display = "none";
            } else {
                document.getElementById(`like-active-${reviewId}`).style.display = "none";
                document.getElementById(`like-inactive-${reviewId}`).style.display = "";
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function toggleDislike(reviewId) {
    fetch(`/reviews/${reviewId}/dislike/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok.');
            }
        })
        .then(data => {
            document.getElementById(`like-count-${reviewId}`).innerText = data.like_count;
            document.getElementById(`dislike-count-${reviewId}`).innerText = data.dislike_count;

            document.getElementById(`like-active-${reviewId}`).style.display = "none";
            document.getElementById(`like-inactive-${reviewId}`).style.display = "";
            if (data.disliked) {
                document.getElementById(`dislike-active-${reviewId}`).style.display = "";
                document.getElementById(`dislike-inactive-${reviewId}`).style.display = "none";
            } else {
                document.getElementById(`dislike-active-${reviewId}`).style.display = "none";
                document.getElementById(`dislike-inactive-${reviewId}`).style.display = "";
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}