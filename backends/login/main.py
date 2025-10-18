# 1. Gerekli kütüphaneleri ve modülleri import et
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends
import requests # requests kütüphanesini import et
import json     # JSON işlemleri için import et

# Firebase Web API Key'ini buraya yapıştır
# GÜVENLİK NOTU: Production ortamında bu anahtarı doğrudan koda yazmak yerine
# ortam değişkenlerinden (environment variables) veya bir config dosyasından okumak daha güvenlidir.
FIREBASE_WEB_API_KEY = "AIzaSyArVmmEeBYNl55gDMno29_RbML03AmSqB0" # firebaseConfig içindeki apiKey

class UserSchema(BaseModel):
    email: str
    password: str

# Login yanıtı için model (sadece idToken döneceğiz)
class LoginResponseSchema(BaseModel):
    idToken: str

# 2. FastAPI uygulamasını oluştur
app = FastAPI()

# CORS ayarları (Mevcut kodun)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Firebase Admin SDK'sını başlat (Mevcut kodun)
SERVICE_ACCOUNT_FILE = 'fastapi-auth-project-411d4-firebase-adminsdk-fbsvc-f6714f210e.json'
try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK başarıyla başlatıldı.")
except Exception as e:
    print(f"HATA: Firebase Admin SDK başlatılamadı! -> {e}")

# Token doğrulama (Mevcut kodun)
token_auth_scheme = HTTPBearer()
def get_current_user(cred: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    # ... (mevcut get_current_user fonksiyonun içeriği) ...
     if not cred:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token bulunamadı",
            headers= {"WWW-Authenticate": "Bearer"}
        )
     try:
        # Gelen token'ı Firebase'e gönderip doğruluğunu kontrol ediyoruz.
        # cred bir HTTPAuthorizationCredentials nesnesi, token'ı almak için .credentials kullanılır.
        token = cred.credentials
        decoded_token = auth.verify_id_token(token)
     except Exception as e:
        # Token geçersiz, süresi dolmuş veya başka bir hata varsa...
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Geçersiz token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
     # Token geçerliyse, içindeki kullanıcı bilgilerini (payload) döndürüyoruz.
     return decoded_token


# 4. Basit bir test endpoint'i (Mevcut kodun)
@app.get("/")
def read_root():
    return {"message": "Merhaba! FastAPI ve Firebase sunucunuz çalışıyor."}

# Signup endpoint'i (Mevcut kodun)
@app.post("/signup", status_code=status.HTTP_201_CREATED)
def create_user(user: UserSchema):
    try:
        new_user = auth.create_user(
            email=user.email,
            password=user.password
        )
        return {"message": "Kullanıcı başarıyla oluşturuldu","uid": new_user.uid}

    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # status==status... kısmını düzelttim
            detail = "Bu email adresi zaten kullanılıyor"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"HATA: Sunucu Hatası: {str(e)}" # Hatayı string'e çevir
        )

# YENİ LOGIN ENDPOINT'İ
@app.post("/login", response_model=LoginResponseSchema)
def login_user(user: UserSchema):
    # Firebase Auth REST API endpoint URL'si
    rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

    # Gönderilecek veri (payload)
    payload = json.dumps({
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    })

    # API isteği için parametreler (Web API Key)
    params = {"key": FIREBASE_WEB_API_KEY}

    try:
        # Firebase REST API'sine POST isteği gönder
        response = requests.post(rest_api_url, params=params, data=payload)
        response.raise_for_status() # HTTP hata kodları için (4xx, 5xx) exception fırlat

        # Başarılı yanıtı işle
        result = response.json()
        id_token = result.get("idToken")

        if not id_token:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase'den idToken alınamadı."
            )

        # Sadece idToken'ı döndür
        return LoginResponseSchema(idToken=id_token)

    except requests.exceptions.RequestException as e:
        # Network hatası veya HTTP hata kodu varsa
        try:
            # Firebase'den gelen hata detayını almaya çalış
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", "Bilinmeyen Firebase hatası")
            print(f"Firebase Auth Hatası: {error_message}") # Hata detayını logla

            # Firebase hata mesajlarına göre özel durumlar
            if "INVALID_PASSWORD" in error_message or "EMAIL_NOT_FOUND" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                 raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="E-posta veya şifre hatalı."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Giriş hatası: {error_message}"
                )
        except (ValueError, AttributeError):
             # Yanıt JSON değilse veya response nesnesi yoksa
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"API isteği sırasında hata: {str(e)}"
            )
    except Exception as e:
        # Diğer beklenmedik hatalar
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beklenmedik bir sunucu hatası oluştu: {str(e)}"
        )


# /me endpoint'i (Mevcut kodun - İçeriğini token doğrulama için get_current_user'a göre ayarladım)
@app.get("/me")
def get_user_profile(user_data: dict = Depends(get_current_user)):
    """
    Bu rota, geçerli bir Bearer token ile korunmaktadır.
    Başarılı bir istekte, token'dan alınan kullanıcı bilgilerini döndürür.
    """
    # user_data, get_current_user fonksiyonundan dönen decoded_token'dır.
    uid = user_data.get("uid")
    email = user_data.get("email")

    # Burada user_data içindeki diğer bilgilere de erişebilirsin (name, picture vb. varsa)
    # Örneğin Firestore'dan bu UID'ye ait ek kullanıcı profil bilgilerini çekebilirsin.
    # Şimdilik sadece email ve uid döndürelim.
    return {"message": f"Bu korumalı bir alandır. Hoş geldin {email}!", "uid": uid, "email": email}


# Uvicorn ile çalıştırmak için (opsiyonel, terminalden de çalıştırılabilir)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)