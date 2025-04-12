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
  }function analyzeFile() {
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
  // Scroll effect for shrinking header
window.addEventListener('scroll', () => {
  const header = document.getElementById('mainHeader');
  const headerContent = document.getElementById('headerContent');

  if (window.scrollY > 100) {
    header.classList.add('header-scrolled');
  } else {
    header.classList.remove('header-scrolled');
  }
});
