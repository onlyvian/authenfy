async function analyzeFile() {
  const fileInput = document.getElementById('file-upload');
  const result = document.getElementById('result');

  if (!fileInput.files.length) {
    result.textContent = "Please upload a file first.";
    result.style.color = "black";
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("video", file);

  result.textContent = "⏳ Analyzing...";
  result.style.color = "black";

  try {
    const response = await fetch("/detect", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Unknown error occurred");
    }

    const data = await response.json();

    result.innerHTML = `
      <strong>${data.label === "FAKE" ? "⚠️ Deepfake Detected!" : "✅ Content is Authentic!"}</strong><br>
      <small>Confidence: ${(data.confidence * 100).toFixed(2)}%</small><br>
      <small>Total Time: ${data.time_taken.total.toFixed(2)}s</small>
    `;
    result.style.color = data.label === "FAKE" ? "red" : "green";

  } catch (err) {
    result.textContent = "❌ Error: " + err.message;
    result.style.color = "red";
  }
}

// Shrinking header scroll effect
window.addEventListener('scroll', () => {
  const header = document.getElementById('mainHeader');
  if (window.scrollY > 100) {
    header.classList.add('header-scrolled');
  } else {
    header.classList.remove('header-scrolled');
  }
});
