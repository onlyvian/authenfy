document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('fileInput');
  const form = document.querySelector('form');
  const resultDiv = document.getElementById('result');
  const analyzeButton = document.getElementById('analyzeBtn');
  const uploadForm = document.getElementById('uploadForm');

  const analyzeUrl = uploadForm.getAttribute('action');

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    if (!fileInput.files.length) {
      resultDiv.innerHTML = '❌ Please upload a file first.';
      resultDiv.style.color = 'red';
      return;
    }

    const formData = new FormData();
    formData.append('media', fileInput.files[0]);  // ✅ FIXED: must match Flask's key

    resultDiv.innerHTML = '⏳ Uploading and analyzing your file...';
    resultDiv.style.color = 'black';

    const xhr = new XMLHttpRequest();
    xhr.open('POST', analyzeUrl, true);

    xhr.onload = function () {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);

        if (response.label && response.time_taken) {
          const resultText = response.label === 'FAKE'
            ? `❌ Result: Fake Video! 🚨`
            : `✅ Result: Real Video!`;

          const analysisTime = parseFloat(response.time_taken.total || 0).toFixed(2);
          resultDiv.innerHTML = `${resultText}<br/>⏱️ Analysis Time: ${analysisTime} seconds`;
          resultDiv.style.color = response.label === 'FAKE' ? 'red' : 'green';
        } else {
          resultDiv.innerHTML = '❌ Unexpected response from server.';
          resultDiv.style.color = 'red';
        }
      } else {
        resultDiv.innerHTML = '❌ Failed to upload the file. Please try again.';
        resultDiv.style.color = 'red';
      }
    };

    xhr.onerror = function () {
      resultDiv.innerHTML = '❌ An error occurred during the upload.';
      resultDiv.style.color = 'red';
    };

    xhr.send(formData);
  });

  fileInput.addEventListener('change', function () {
    if (fileInput.files.length > 0) {
      resultDiv.innerHTML = `Ready to upload: ${fileInput.files[0].name}`;
      resultDiv.style.color = 'black';
    }
  });
});
