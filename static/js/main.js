document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSection = document.getElementById('loadingSection');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const successSection = document.getElementById('successSection');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            // Show loading section, hide others
            loadingSection.classList.remove('d-none');
            errorSection.classList.add('d-none');
            successSection.classList.add('d-none');
            analyzeBtn.disabled = true;

            // Make API request to analyze the repository
            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading section
                loadingSection.classList.add('d-none');
                
                if (data.status === 'error') {
                    // Show error section
                    errorSection.classList.remove('d-none');
                    errorMessage.textContent = data.message;
                } else {
                    // Show success section
                    successSection.classList.remove('d-none');
                }
                
                analyzeBtn.disabled = false;
            })
            .catch(error => {
                // Hide loading section, show error
                loadingSection.classList.add('d-none');
                errorSection.classList.remove('d-none');
                errorMessage.textContent = 'An unexpected error occurred: ' + error.message;
                analyzeBtn.disabled = false;
            });
        });
    }
});
