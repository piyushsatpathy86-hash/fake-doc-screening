// script.js
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const fileInput = document.getElementById('passportImage');
  const file = fileInput.files[0];
  if (!file) return alert('Please select a passport image.');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/api/scan', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    document.getElementById('result').innerHTML = `
      <p><strong>Risk Score:</strong> ${data.risk_score || 'N/A'}</p>
      <p><strong>Status:</strong> ${data.status || 'Checked'}</p>
      <p><a href="/report/${data.id}" target="_blank">📄 PDF Report</a></p>
    `;
  } catch (err) {
    document.getElementById('result').textContent = 'Error: ' + err.message;
  }
});