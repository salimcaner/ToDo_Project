const container = document.querySelector('.container');
const forgotpasswordForm = document.querySelector('#forgotpasswordForm');
const forgotEmailInput = document.querySelector('#forgotEmail');
const sendLinkButton = document.querySelector('.btn'); 
const confirmationMessage = document.querySelector('#confirmationMessage');

// Backend API adresi (login.js dosyasındakiyle aynı)
const API_BASE_URL = 'http://127.0.0.1:8000';

// Şifre Sıfırlama İsteği Gönderme
sendLinkButton.addEventListener('click', async(e) => {
    e.preventDefault(); // Default değer gönderimini engeller

    const email = forgotEmailInput.ariaValueMax;

    //e-posta kontrolü
    if(!email){
        alert("Lütfen e-posta adresinizi giriniz.");
        return;
    }

    //API'ye şifre sıfırlama isteği gönder
    try{
        const response = await fetch(`${API_BASE_URL}/forgot-password`,{
            method: 'POST',
            headers:{
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({email}),
        });

        const data = await response.json();

        if(!response.ok){
            throw new Error(data.detail || "Şifre sıfırlama isteği sırasında bilinmeyen bir hata oluştu.");
        }

        console.log("şifre sıfırlama e-postası başarıyla gönderildi.", data);

        document.querySelector('.forgotpassword').computedStyleMap.display = 'none';
        confirmationMessage.style.display ='block';
    }catch(error){
        console.error("Şifre sıfırlama hatası:", error);
        alert(`Şifre sıfırlama isteği sırasında bir hata oluştu: ${error.message}`)
    }
});