<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Defect Detection</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    .image-box { max-width: 100%; max-height: 300px; object-fit: contain; border: 1px solid #ccc; }
  </style>
</head>
<body class="p-4">
  <div class="container">
    <h2 class="mb-4">Image Defect Detection</h2>
    
    <form id="upload-form">
      <input type="file" id="image-input" accept="image/*" class="form-control mb-3" required>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>

    <div id="result-section" class="mt-4 d-none">
      <div class="row">
        <div class="col-md-6">
          <h5>Input Image</h5>
          <img id="input-preview" class="image-box" />
        </div>
        <div class="col-md-6">
          <h5>Output Image</h5>
          <img id="output-preview" class="image-box" />
        </div>
      </div>

      <div class="mt-4">
        <h5>Defect Summary</h5>
        <ul id="defect-list" class="list-group"></ul>
      </div>
    </div>
  </div>

  <script>
    document.getElementById('upload-form').addEventListener('submit', async function(e) {
      e.preventDefault();

      const fileInput = document.getElementById('image-input');
      const file = fileInput.files[0];

      if (!file) return;

      document.getElementById('input-preview').src = URL.createObjectURL(file);

      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/predict', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      document.getElementById('output-preview').src = `data:image/png;base64,${data.output_image}`;

      const defectList = document.getElementById('defect-list');
      defectList.innerHTML = '';

      const defects = {...data.Cleanliness, ...data.Neatness};
      for (const [cls, count] of Object.entries(defects)) {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = `${cls}: ${count}`;
        defectList.appendChild(li);
      }

      document.getElementById('result-section').classList.remove('d-none');
    });
  </script>
</body>
</html>
