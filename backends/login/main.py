# 1. Gerekli kütüphaneleri ve modülleri import et
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends

class UserSchema(BaseModel):
    email: str
    password: str

# 2. FastAPI uygulamasını oluştur
app = FastAPI()

# Frontend'den gelen isteklere izin vermek için CORS ayarları (Geliştirme aşamasında hepsi açık)
# Production'a geçerken origins listesini sadece kendi frontend adresinizle sınırlamanız ÖNEMLİDİR.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Firebase Admin SDK'sını başlat
# İndirdiğimiz ve adını değiştirdiğimiz servis anahtarı dosyasının yolu
SERVICE_ACCOUNT_FILE = 'fastapi-auth-project-411d4-firebase-adminsdk-fbsvc-f6714f210e.json'

try:
    # Credentials nesnesini oluştur
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    # Firebase uygulamasını başlat
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK başarıyla başlatıldı.")
except Exception as e:
    print(f"HATA: Firebase Admin SDK başlatılamadı! -> {e}")
    # Uygulama Firebase olmadan çalışamaz, bu yüzden burada durdurabiliriz.
    # Geliştirme aşamasında hatayı görmek için programı durdurmamak daha iyi olabilir.
    # import sys
    # sys.exit(1)


token_auth_scheme = HTTPBearer()

def get_current_user(cred: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):

#Gelen Bearer token'ını alır, Firebase ile doğrular ve kullanıcı bilgilerini döndürür.
#Eğer token geçersizse veya yoksa, bir hata fırlatır.

    if not cred:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token bulunamadı",
            headers= {"WWW-Authenticate": "Bearer"}
        )
    try:
        ## Gelen token'ı Firebase'e gönderip doğruluğunu kontrol ediyoruz.
        token = cred.get_credential()
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


# 4. Basit bir test endpoint'i (API rotası) oluştur
# Bu adres, sunucunun çalışıp çalışmadığını kontrol etmemizi sağlar.
@app.get("/")
def read_root():
    return {"message": "Merhaba! FastAPI ve Firebase sunucunuz çalışıyor."}


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
            status_code=status==status.HTTP_400_BAD_REQUEST,
            detail = "Bu email adresi zaten kullanılıyor"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"HATA: Sunucu Hatası"
        )

@app.get("/me")
def get_user_profile(user_data: dict = Depends(get_current_user)):
    """
    Bu rota, geçerli bir Bearer token ile korunmaktadır.
    Başarılı bir istekte, token'dan alınan kullanıcı bilgilerini döndürür.
    """
    # user_data, get_current_user fonksiyonundan dönen decoded_token'dır.
    # Bu bilgi sayesinde kimin istek yaptığını bilebiliriz.
    uid = user_data.get("uid")
    email = user_data.get("email")

    return {"message": f"Bu korumalı bir alandır. Hoş geldin {email}!", "uid": uid}


