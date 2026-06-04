# HomeLak

Django alapú ingatlanhirdetési webalkalmazás portfólió- és beadandóprojekt célra.

## Projekt röviden

A **HomeLak** egy olyan webalkalmazás, ahol a felhasználók ingatlanhirdetéseket böngészhetnek, kereshetnek és szűrhetnek közöttük, majd regisztráció és bejelentkezés után saját hirdetéseket is létrehozhatnak, szerkeszthetnek és törölhetnek.

A projekt célja az volt, hogy egy valós felhasználási helyzetre épülő, jól strukturált Django alkalmazás készüljön, amely egyszerre mutatja meg:

- a modellkezelést,
- az űrlapkezelést,
- a felhasználóhitelesítést,
- a jogosultságkezelést,
- a fájlfeltöltést,
- a validációkat,
- az automatizált tesztelést,
- és egy több oldalas, egységes webes felület kialakítását.

---

## Fő funkciók

### Nyilvános funkciók
- főoldal a legfrissebb ingatlanokkal,
- ingatlanok listázása,
- keresés és szűrés:
  - település szerint,
  - minimum ár szerint,
  - maximum ár szerint,
  - minimum szobaszám szerint,
- rendezés:
  - legújabbak,
  - ár növekvő,
  - ár csökkenő,
  - több szoba elöl,
  - nagyobb alapterület elöl,
- lapozás az ingatlanlistán,
- ingatlan részletező oldal,
- fő kép és galéria megjelenítése,
- regisztráció,
- bejelentkezés és kijelentkezés.

### Bejelentkezett felhasználói funkciók
- saját hirdetés létrehozása,
- saját hirdetés szerkesztése,
- saját hirdetés törlése,
- saját fiók oldal,
- dashboard a saját fiókban, amely mutatja:
  - saját hirdetések száma,
  - kedvencek száma,
  - beérkezett üzenetek száma,
  - összes galériakép száma,
  - legutóbbi saját hirdetések,
  - legutóbbi beérkezett üzenetek,
- ingatlanok kedvencekhez adása és eltávolítása,
- külön kedvencek oldal,
- kapcsolatfelvétel más felhasználó hirdetéséhez kapcsolódóan,
- beérkezett üzenetek megtekintése.

### Admin funkciók
- Django adminfelület,
- ingatlanok kezelése,
- galériaképek inline kezelése,
- üzenetek kezelése,
- kedvencek áttekintése.

---

## Használt technológiák

- **Python 3**
- **Django**
- **SQLite**
- **HTML**
- **CSS**
- **Pillow**

---

## Adatmodell röviden

### Property
Egy ingatlanhirdetést reprezentál.

Fő mezők:
- feltöltő felhasználó,
- cím,
- település,
- ár,
- alapterület,
- szobák száma,
- leírás,
- kép URL,
- feltöltött fő kép,
- létrehozás ideje.

### PropertyImage
Egy ingatlan galériaképeit tárolja.

### Favorite
Felhasználó és ingatlan kapcsolat a kedvencek funkcióhoz.

### ContactMessage
Felhasználók közötti, ingatlanhoz kötött üzenetek tárolása.

---

## Validációk és szabályok

A projektben több szinten is történik adatellenőrzés.

### Számmezők
Az alábbi mezők nem lehetnek 0 vagy negatív értékűek:
- ár,
- alapterület,
- szobák száma.

### Képfeltöltés
A feltöltött képekre az alábbi szabályok vonatkoznak:
- maximum **5 MB** fájlméret,
- csak tipikus képtípusok engedélyezettek:
  - JPG
  - JPEG
  - PNG
  - WEBP
  - GIF
- ellenőrzés történik:
  - kiterjesztésre,
  - MIME típusra,
  - és arra is, hogy a fájl valóban képfájl-e.

### Képfájl-takarítás
- ha a fő kép cserélődik, a régi fájl törlődik,
- ha egy galériakép törlődik, a hozzá tartozó fájl is törlődik,
- ha egy ingatlan törlődik, a hozzá tartozó képfájlok is törlődnek.

### Jogosultságkezelés
- saját fiók oldal csak bejelentkezve érhető el,
- hirdetést létrehozni csak bejelentkezett felhasználó tud,
- szerkeszteni és törölni csak a tulajdonos tud,
- saját hirdetésre nem lehet üzenetet küldeni,
- kedvencek funkció csak bejelentkezett felhasználónak érhető el.

---

## Projektstruktúra

```text
homelak_project/
├── core/
├── listings/
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
├── README.md
└── .env.example
```

### Fontosabb részek
- `core/` – projektbeállítások, globális URL-ek
- `listings/` – modellek, formok, view-k, URL-ek, admin, tesztek
- `templates/` – HTML sablonok
- `static/` – stíluslapok
- `media/` – feltöltött képek
- `tests.py` – automatizált tesztek

---

## Telepítés és futtatás

### 1. Projekt letöltése
Klónozd a repositoryt vagy töltsd le ZIP-ben.

```bash
git clone <repo-url>
cd homelak_project
```

### 2. Virtuális környezet létrehozása
Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Függőségek telepítése

```bash
pip install -r requirements.txt
```

### 4. Környezeti változók beállítása
Másold le az `.env.example` fájlt `.env` néven.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 5. Migrációk futtatása

```bash
python manage.py migrate
```

### 6. Admin felhasználó létrehozása

```bash
python manage.py createsuperuser
```

### 7. Fejlesztői szerver indítása

```bash
python manage.py runserver
```

Ezután az alkalmazás elérhető itt:

```text
http://127.0.0.1:8000/
```

Admin felület:

```text
http://127.0.0.1:8000/admin/
```

---

## Környezeti változók

A projekt `.env` fájlból vagy rendszerkörnyezeti változókból is képes dolgozni.

### Példa `.env`

```env
SECRET_KEY=egy-hosszu-egyedi-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=

LANGUAGE_CODE=hu
TIME_ZONE=Europe/Budapest

SQLITE_NAME=db.sqlite3
STATIC_URL=/static/
STATIC_ROOT=staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=media
```

### Production példa

```env
SECRET_KEY=egy-valodi-production-secret-key
DEBUG=False
ALLOWED_HOSTS=sajat-domain.hu,www.sajat-domain.hu
CSRF_TRUSTED_ORIGINS=https://sajat-domain.hu,https://www.sajat-domain.hu
```

---

## Tesztek futtatása

A projekt automatizált teszteket tartalmaz.

Futtatás:

```bash
python manage.py test
```

Hasznos ellenőrzések:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

A jelenlegi állapotban a projekt **42 sikeres automatizált teszttel** rendelkezik.

A tesztek többek között lefedik:
- modellvalidáció,
- jogosultságkezelés,
- CRUD műveletek,
- szűrés és keresés,
- kedvencek,
- kapcsolatfelvétel,
- dashboard,
- képfeltöltési validáció,
- fájltakarítás,
- galériaképek kezelése.

---

## Gyors funkcionális tesztelés

### Alap használat
1. Regisztrálj vagy lépj be.
2. Hozz létre egy új hirdetést.
3. Tölts fel fő képet és több galériaképet.
4. Nézd meg a részletező oldalon a galériát.
5. Add kedvencekhez egy másik ingatlant.
6. Küldj üzenetet egy másik felhasználó hirdetésére.
7. Nézd meg a saját fiók dashboardját.
8. Ellenőrizd a kedvencek és üzenetek oldalakat.

---

## Lehetséges továbbfejlesztések

- élő deploy,
- REST API,
- szerepkörök bővítése,
- státuszmező ingatlanokhoz,
- olvasott / olvasatlan üzenetek,
- fejlettebb kereső,
- térképes megjelenítés,
- statisztikák,
- több frontend interakció JavaScript segítségével.

---

## Portfólió szempontból kiemelhető részek

Ez a projekt jól bemutatja:
- Django MVT felépítés használatát,
- relációs adatmodellezést,
- hitelesítést és jogosultságkezelést,
- fájlfeltöltést és fájlkezelést,
- backend validációt,
- adminfelület használatát,
- automatizált tesztelést,
- több oldalas, egységes webes UI kialakítását.

---

## Készítette

- Mászlai Gábor
- Tóth Milán András
