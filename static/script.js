// Sayfa tamamen yüklendiğinde çalışacak kod bloğu
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('greetForm');
  const nameInput = document.querySelector('input[name="name"]');
  const surnameInput = document.querySelector('input[name="surname"]');
  const messageDiv = document.getElementById('greetMessage');

  form.addEventListener('submit', function (e) {
    e.preventDefault(); // Sayfanın yeniden yüklenmesini engelle

    // Inputlardan alınan değerler
    const name = nameInput.value.trim();
    const surname = surnameInput.value.trim();

    // Basit doğrulama
    if (!name) {
      messageDiv.textContent = "Lütfen adınızı girin.";
      messageDiv.style.backgroundColor = "#f8d7da";  // kırmızımsı
      messageDiv.style.borderColor = "#dc3545";
      messageDiv.style.color = "#721c24";
      messageDiv.style.display = "block";
      return;
    }

    // Fetch ile POST isteği
    fetch('/api/greet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: name, surname: surname })
    })
    .then(response => {
      if (!response.ok) {
        // Hata mesajını JSON veya text dönebilir; önce JSON deniyoruz
        return response.text().then(text => { throw new Error(text); });
      }
      return response.json();
    })
    .then(data => {
      // Dönen JSON: { "message": "Selam name surname" }
      messageDiv.textContent = data.message;
      messageDiv.style.backgroundColor = "#e9f7ef";  // yeşilimsi
      messageDiv.style.borderColor = "#28a745";
      messageDiv.style.color = "#155724";
      messageDiv.style.display = "block";
    })
    .catch(err => {
      // Hata durumunda kullanıcıya bilgi ver
      messageDiv.textContent = `Hata: ${err.message}`;
      messageDiv.style.backgroundColor = "#f8d7da";  // kırmızımsı
      messageDiv.style.borderColor = "#dc3545";
      messageDiv.style.color = "#721c24";
      messageDiv.style.display = "block";
    });
  });
});
