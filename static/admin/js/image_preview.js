document.addEventListener('DOMContentLoaded', function(){
  const input = document.querySelector('input[name="image_url"]');
  if(!input) return;

  function ensurePreviewContainer(){
    let img = document.getElementById('product-image-preview-img');
    const placeholder = document.getElementById('product-image-preview');
    if(!img){
      if(placeholder){
        placeholder.innerHTML = '<img id="product-image-preview-img" style="width:100px;height:140px;object-fit:cover;border-radius:4px;"/>';
        img = document.getElementById('product-image-preview-img');
      }
    }
    return img;
  }

  function updatePreview(url){
    const img = ensurePreviewContainer();
    if(!img) return;
    if(!url){
      img.removeAttribute('src');
      img.style.display = 'none';
      const parent = document.getElementById('product-image-preview');
      if(parent) parent.textContent = '(no image)';
      return;
    }
    img.style.display = '';
    img.src = url;
    // clear placeholder text if present
    const parent = document.getElementById('product-image-preview');
    if(parent) parent.textContent = '';
  }

  // initialize with current value
  updatePreview(input.value);

  // live update as user types
  input.addEventListener('input', function(e){
    const url = e.target.value.trim();
    updatePreview(url);
  });

  // also update when focus leaves (useful for paste/autofill)
  input.addEventListener('change', function(e){
    updatePreview(e.target.value.trim());
  });
});