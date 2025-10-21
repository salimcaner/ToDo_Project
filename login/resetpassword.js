const resetpasswordForm = document.querySelector('#resetpasswordForm');
const newPasswordInput = document.querySelector('#newPassword');
const confirmNewPasswordInput = document.querySelector('#confirmNewPassword');

const API_BASE_URL = 'http://127.0.0.1:8000';

resetpasswordForm.addEventListener('submit', async (e) => {
    e.preventDefault(); 

    const newPassword = newPasswordInput.value;
    const confirmNewPassword = confirmNewPasswordInput.value;

    // URL'den token'ı al
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token'); // E-posta linkindeki token'ı okur

    if (!token) {
        alert("Geçersiz veya eksik şifre sıfırlama bağlantısı.");
        return;
    }

    if (newPassword !== confirmNewPassword) {
        alert("Girdiğiniz şifreler eşleşmiyor.");
        return;
    }
    
    if (newPassword.length < 6) { // Örnek şifre uzunluğu kontrolü
        alert("Şifre en az 6 karakter olmalıdır.");
        return;
    }

    try {
        // API'ye şifre güncelleme isteği gönder
        const response = await fetch(`${API_BASE_URL}/reset-password`, { // Endpoint'i varsayımsal olarak '/reset-password' olarak belirledik
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // Backend'in token ve yeni şifreyi beklediğini varsayıyoruz
            body: JSON.stringify({ token, new_password: newPassword }), 
        });

        const data = await response.json(); 

        if (!response.ok) {
            // Sunucudan gelen hata mesajını göster
            throw new Error(data.detail || "Şifre güncelleme sırasında bilinmeyen bir hata oluştu.");
        }

        // Güncelleme başarılı olduğunda:
        console.log("Şifre başarıyla güncellendi.", data);
        alert("Şifreniz başarıyla güncellendi! Lütfen yeni şifrenizle giriş yapın.");
        
        // Kullanıcıyı login sayfasına yönlendir
        window.location.href = 'login.html'; 

    } catch (error) {
        // Hata durumunda
        console.error("Şifre güncelleme hatası:", error);
        alert(`Şifre güncelleme sırasında bir hata oluştu: ${error.message}`);
    }
});