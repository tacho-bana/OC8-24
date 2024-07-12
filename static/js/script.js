document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('file-input');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    const colors = JSON.parse(data.colors);
    startDynamicBackground(colors);
});

function updateBackgroundColor(colors, index) {
    const color = colors[index];
    document.body.style.backgroundColor = `rgba(${color[0] * 255}, ${color[1] * 255}, ${color[2] * 255}, ${color[3]})`;
}

function startDynamicBackground(colors) {
    let index = 0;
    setInterval(() => {
        updateBackgroundColor(colors, index);
        index = (index + 1) % colors.length;
    }, 1000);
}
