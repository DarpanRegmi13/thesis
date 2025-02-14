document.addEventListener('DOMContentLoaded', function () {
    // Load the list of PDFs for managing them (delete section)
    async function loadPdfList() {
        try {
            const response = await fetch('http://127.0.0.1:5005/list_pdfs');
            const data = await response.json();
            const selectElement = document.getElementById('delete-file');

            // Clear any previous options
            selectElement.innerHTML = '';

            // Add a default "Choose a PDF" option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Choose a PDF';
            selectElement.appendChild(defaultOption);

            // Check if there are PDFs available
            if (data.pdfs.length > 0) {
                // Add a dropdown option for each PDF
                data.pdfs.forEach(pdf => {
                    const option = document.createElement('option');
                    option.value = pdf;
                    option.textContent = pdf;
                    selectElement.appendChild(option);
                });
            } else {
                const noPdfsOption = document.createElement('option');
                noPdfsOption.textContent = 'No PDFs available for deletion';
                selectElement.appendChild(noPdfsOption);
            }
        } catch (error) {
            console.error('Error loading PDF list:', error);
            // Provide feedback in case of failure
            const deleteMessage = document.getElementById('delete-message');
            deleteMessage.innerHTML = 'Failed to load PDF list. Please try again.';
            deleteMessage.style.color = 'red';
        }
    }

    // Handle Delete PDF form submission
    const deletePdfForm = document.getElementById('delete-pdf-form');
    const deleteMessage = document.getElementById('delete-message');
    
    deletePdfForm.addEventListener('submit', async function (event) {
        event.preventDefault();  // Prevent the default form submission

        const filename = document.getElementById('delete-file').value;  // Get the selected filename
        if (!filename) {
            deleteMessage.innerHTML = 'Please select a PDF to delete.';
            deleteMessage.style.color = 'red';
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5005/delete_pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename: filename }),  // Send the filename as JSON
            });

            const data = await response.json();
            if (data.success) {
                deleteMessage.innerHTML = `PDF "${filename}" deleted successfully.`;
                deleteMessage.style.color = 'green';
                loadPdfList();  // Reload the PDF list after deletion
            } else {
                // If an error occurs (like PDF not found)
                deleteMessage.innerHTML = `Error: ${data.error || 'Unknown error'}`;
                deleteMessage.style.color = 'red';
            }
        } catch (error) {
            deleteMessage.innerHTML = 'Something went wrong. Please try again.';
            deleteMessage.style.color = 'red';
        }
    });

    // Initial load of PDFs when the page loads
    loadPdfList();
});

document.addEventListener('DOMContentLoaded', function () {
    const reloadBtn = document.getElementById('reload-btn');
    const reloadStatus = document.getElementById('reload-status');

    if (reloadBtn) {
        reloadBtn.addEventListener('click', async function () {
            reloadStatus.innerText = 'Reloading PDFs... Please wait.';
            reloadStatus.style.color = 'blue';

            try {
                const response = await fetch('http://127.0.0.1:5005/reload_pdfs', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();
                reloadStatus.innerText = data.message;
                reloadStatus.style.color = 'green';
            } catch (error) {
                console.error("Error:", error);
                reloadStatus.innerText = "Failed to reload PDFs.";
                reloadStatus.style.color = 'red';
            }
        });
    }
});
