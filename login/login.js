//Eleman Seçimi
const container = document.querySelector('.container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');
//Kayıt formu eleman seçimi
const registerForm = document.querySelector('#registerForm');
const registerEmail = document.querySelector('#registerEmail');
const registerPassword = document.querySelector('#registerPassword');
//Giriş Formu Elemen Seçimi
const loginForm = document.querySelector('#loginForm');
const loginEmail = document.querySelector('#loginEmail');
const loginPassword = document.querySelector('#loginPassword');

registerBtn.addEventListener('click', ()=>{
    container.classList.add('active');
});

loginBtn.addEventListener('click', () =>{
    container.classList.remove('active');
});

//Backend API adresi
const API_BASE_URL = 'http://127.0.0.1:8000';

//kayıt Formu Gönderildiğinde Çalışacak Fonksiyon
registerForm.addEventListener('submit', async (e) =>{
    e.preventDefault(); //Default değer gönderimini engelle

    const email = registerEmail.value;
    const password = registerPassword.value;

    try{
        const response = await fetch(`${API_BASE_URL}/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password}),
        });
        const data = await response.json();

        if(!response.ok){
            throw new Error(data.detail || "Bilinmeyen bir sunucu hatası oluştu.");
        }

        // Kayıt başarılı olduğunda
        console.log("Kayıt başarılı!", data); // Backend'den gelen mesajı logla (örn: {"message": "...", "uid": "..."})
        alert("Kayıt başarıyla tamamlandı! Giriş yapabilirsiniz.");
        registerEmail.value = ''; // Inputları temizle
        registerPassword.value = '';
        container.classList.remove('active'); // Giriş formunu göster

    } catch (error) {
        // Kayıt sırasında hata olursa (network veya sunucu hatası)
        console.error("Kayıt hatası:", error);
        alert(`Kayıt sırasında bir hata oluştu: ${error.message}`);
    }
});
// Giriş formu gönderildiğinde çalışacak fonksiyon
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Formun varsayılan gönderme işlemini engelle

    const email = loginEmail.value;
    const password = loginPassword.value;

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json(); // Yanıtı JSON olarak al

        if (!response.ok) {
            // Sunucudan gelen hata mesajını göster (FastAPI'deki detail)
            throw new Error(data.detail || 'Bilinmeyen bir sunucu hatası oluştu.');
        }

        // Giriş başarılı olduğunda (backend sadece idToken dönüyor)
        console.log("Giriş başarılı!");
        const idToken = data.idToken;
        console.log("Alınan ID Token:", idToken);

        // Token'ı localStorage'a kaydet
        localStorage.setItem('firebaseIdToken', idToken);

        alert("Giriş başarıyla yapıldı!");
        loginEmail.value = ''; // Inputları temizle
        loginPassword.value = '';

        // Kullanıcıyı ana sayfaya yönlendir
        window.location.href = '/html/home.html'; // veya projenin ana sayfası

    } catch (error) {
        // Giriş sırasında hata olursa (network veya sunucu hatası)
        console.error("Giriş hatası:", error);
        alert(`Giriş sırasında bir hata oluştu: ${error.message}`);
    }
});



