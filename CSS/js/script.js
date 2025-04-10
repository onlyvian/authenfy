function analyzeFile() {
    const fileInput = document.getElementById('file-upload');
    const result = document.getElementById('result');
  
    if (!fileInput.files.length) {
      result.textContent = "Please upload a file first.";
      return;
    }
  
    // Fake analysis simulation
    result.textContent = "Analyzing...";
    setTimeout(() => {
      const isFake = Math.random() < 0.5;
      result.textContent = isFake
        ? "⚠️ Deepfake Detected!"
        : "✅ Content is Authentic!";
      result.style.color = isFake ? "red" : "green";
    }, 1500);
  }