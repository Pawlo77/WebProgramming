
function toggleLike(reviewId, currentState) {
    let url = currentState === 'true' ? "{% url 'remove_like' %}" : "{% url 'add_like' %}";  // Replace with your actual URLs
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ review_id: reviewId })
    })
        .then(response => {
            if (response.ok) {
                // Update the UI accordingly
                location.reload();  // Reload to reflect the changes
            } else {
                console.error("Error toggling like:", response.statusText);
            }
        })
        .catch(error => console.error("Error:", error));
}

function toggleDislike(reviewId, currentState) {
    let url = currentState === 'true' ? "{% url 'remove_dislike' %}" : "{% url 'add_dislike' %}";  // Replace with your actual URLs
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ review_id: reviewId })
    })
        .then(response => {
            if (response.ok) {
                // Update the UI accordingly
                location.reload();  // Reload to reflect the changes
            } else {
                console.error("Error toggling dislike:", response.statusText);
            }
        })
        .catch(error => console.error("Error:", error));
}