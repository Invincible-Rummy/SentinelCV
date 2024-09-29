// Custom JavaScript for Patient Position Monitor
document.addEventListener('DOMContentLoaded', function() {
    console.log('Patient Position Monitor is ready.');
    
    // Add event listeners to reset buttons
    const resetButtons = document.querySelectorAll('.reset-btn');
    resetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const positionCell = row.querySelector('td:nth-child(2)');
            const statusCell = row.querySelector('td:nth-child(3)');
            
            // Reset position to 0 minutes
            positionCell.textContent = '0 min';
            
            // Reset status to Normal
            statusCell.innerHTML = '<span class="badge badge-success">Normal</span>';
            
            // Animate the reset button
            this.classList.add('btn-success');
            this.innerHTML = '<i class="fas fa-check mr-1"></i>Reset';
            
            setTimeout(() => {
                this.classList.remove('btn-success');
                this.innerHTML = '<i class="fas fa-undo mr-1"></i>Reset';
            }, 1000);
        });
    });

    // Simulate position changes (for demonstration purposes)
    setInterval(() => {
        const rows = document.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const positionCell = row.querySelector('td:nth-child(2)');
            const statusCell = row.querySelector('td:nth-child(3)');
            let currentPosition = parseInt(positionCell.textContent);
            currentPosition += Math.floor(Math.random() * 3); // Increase by 0, 1, or 2 minutes
            positionCell.textContent = currentPosition + ' min';

            // Update status based on position
            if (currentPosition < 30) {
                statusCell.innerHTML = '<span class="badge badge-success">Normal</span>';
            } else if (currentPosition < 60) {
                statusCell.innerHTML = '<span class="badge badge-warning">Caution</span>';
            } else {
                statusCell.innerHTML = '<span class="badge badge-danger">Alert</span>';
            }
        });
    }, 5000); // Update every 5 seconds
});