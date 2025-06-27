fetch(`/api/v1/results/today`)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    console.log(data);
    document.getElementById("todays-solution").innerText = data.solution
    document.getElementById("todays-solved").innerText = data.solved ? `YES! (${data.attempt.length} guesses)` : "NO 😢"
    const attemptsOl = document.getElementById("todays-attempts")
    data.attempt.forEach((attempt, _) => {
      const attemptLi = document.createElement("li")
      attemptLi.innerText = attempt
      attemptsOl.appendChild(attemptLi)
    });
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
  });

  document.addEventListener('DOMContentLoaded', function() {
    const spoiler = document.getElementsByClassName('spoiler-warning')
    const toggleBtn = document.getElementById('toggleResults');
    const resultsDiv = document.getElementById('todays-results');
    let resultsVisible = false;
    
    function animateAttempts() {
        const attempts = document.querySelectorAll('#todays-attempts li');
        attempts.forEach((attempt, index) => {
            attempt.style.animation = `popIn 0.4s ease-out ${index * 0.2}s both`;
        });
    }
    
    toggleBtn.addEventListener('click', function() {
        resultsVisible = !resultsVisible;
        
        if (resultsVisible) {
            resultsDiv.style.display = 'block';
            toggleBtn.innerHTML = 'Hide Results <span class="icon">▼</span>';
            toggleBtn.classList.add('active');
            animateAttempts();
            spoiler[0].style.display = "none"
        } else {
            resultsDiv.style.display = 'none';
            toggleBtn.innerHTML = 'Show Results <span class="icon">▼</span>';
            toggleBtn.classList.remove('active');
            spoiler[0].style.display = "block"
        }
    });
});