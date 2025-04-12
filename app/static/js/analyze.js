document.getElementById("analyzeBtn").addEventListener("click", function () {
    const file = document.getElementById("media").files[0];
    const status = document.getElementById("status");
  
    if (!file) {
      status.textContent = "Please select a file to analyze.";
      return;
    }
  
    status.textContent = `Analyzing ${file.name}... (This is a simulation)`;
  
    // You can replace this with an actual request to your backend
    setTimeout(() => {
      status.textContent = `Analysis complete! ✅ (${file.type})`;
    }, 2000);
  });
  