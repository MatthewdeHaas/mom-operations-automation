function download() {
  const week = document.querySelector('input[name=week]').value;
  const url = `/download/${week}`;

  const link = document.createElement('a');
  link.href = url;
  link.download = `week_${week}.zip`; 
  document.body.appendChild(link);
  link.style.display = 'none';
  link.click();
  document.body.removeChild(link);
}

function showSpinner() {
  document.getElementById("loading").classList.remove("hidden");
}

function hideSpinner() {
  document.getElementById("loading").classList.add("hidden");
}
