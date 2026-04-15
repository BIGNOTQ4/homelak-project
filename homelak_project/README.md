# HomeLak

HomeLak egy Django alapú ingatlanhirdetési webalkalmazás, amelyben a felhasználók regisztrálhatnak, bejelentkezhetnek, saját hirdetéseket adhatnak fel, szerkeszthetik vagy törölhetik azokat, valamint böngészhetnek az elérhető ingatlanok között.

## Projekt célja

A projekt célja egy egyszerű, átlátható és jól használható ingatlanos weboldal elkészítése volt, amely bemutatja a Django keretrendszer alapvető használatát:

- felhasználókezelés
- adatbázis-kezelés modellekkel
- CRUD műveletek
- sablonkezelés
- űrlapok és validáció
- képfeltöltés
- keresés és szűrés

## Fő funkciók

### Látogatói funkciók
- főoldal megjelenítése
- elérhető ingatlanok listázása
- ingatlan részletező oldal megtekintése
- keresés és szűrés település, ár és szobaszám alapján
- rendezés ár, alapterület és szobaszám szerint

### Felhasználói funkciók
- regisztráció
- bejelentkezés / kijelentkezés
- saját fiók oldal
- saját hirdetés feladása
- saját hirdetés szerkesztése
- saját hirdetés törlése
- képfeltöltés fájlból vagy kép URL megadása

### Admin funkciók
- ingatlanok kezelése az admin felületen
- felhasználók kezelése
- új ingatlanok hozzáadása adminból

## Használt technológiák

- **Python 3**
- **Django 5**
- **SQLite3**
- **HTML5**
- **CSS3**
- **Pillow** a képfeltöltés kezeléséhez

## Projekt felépítése

```text
HomeLak/
├── core/                  # projektbeállítások, fő URL-ek
├── listings/              # ingatlanokkal kapcsolatos app
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/             # HTML sablonok
├── static/                # CSS fájlok
├── media/                 # feltöltött képek
├── manage.py
├── requirements.txt
└── README.md
```

## Adatmodell

A projekt központi modellje a `Property`, amely az ingatlanok adatait tárolja.

### Tárolt adatok
- feltöltő felhasználó
- cím
- település
- ár
- alapterület
- szobák száma
- leírás
- kép URL
- feltöltött kép
- létrehozás dátuma

## Validációk

A projektben a számmezők validálva vannak, ezért az alábbi mezők csak **pozitív, 0-nál nagyobb értéket** fogadnak el:

- ár
- alapterület
- szobák száma

Ez ellenőrizve van:
- űrlapszinten
- modellszinten
- adatbázis-szinten is

## Telepítés és futtatás

### 1. A projekt letöltése vagy kicsomagolása
Csomagold ki a projektet egy külön mappába.

### 2. Függőségek telepítése
```bash
pip install -r requirements.txt
```

### 3. Migrációk futtatása
```bash
python manage.py migrate
```

### 4. Admin felhasználó létrehozása
```bash
python manage.py createsuperuser
```

### 5. Fejlesztői szerver indítása
```bash
python manage.py runserver
```

### 6. Elérés böngészőből
- Weboldal: `http://127.0.0.1:8000/`
- Admin felület: `http://127.0.0.1:8000/admin/`

## Használat

### Regisztráció és bejelentkezés
A felhasználó a felső menüből tud regisztrálni vagy bejelentkezni.

### Hirdetés feladása
Bejelentkezés után elérhető a **Hirdetés feladása** menüpont, ahol új ingatlan vehető fel.

### Saját hirdetések kezelése
A **Saját fiók** oldalon a felhasználó megtekintheti a saját hirdetéseit, és azokat:
- szerkesztheti
- törölheti

### Keresés és szűrés
Az ingatlanok listájában lehetőség van:
- település szerinti keresésre
- minimum és maximum ár megadására
- minimum szobaszám szerinti szűrésre
- különféle rendezések használatára

## Jogosultságkezelés

A projektben bizonyos műveletek csak bejelentkezett felhasználók számára érhetők el.

Csak a hirdetés tulajdonosa jogosult:
- a saját hirdetés szerkesztésére
- a saját hirdetés törlésére

## Képek kezelése

A hirdetésekhez kétféleképpen lehet képet megadni:

1. **Kép URL** megadásával
2. **Fájl feltöltésével**

Ha feltöltött kép van, a rendszer azt használja elsődlegesen. Ha nincs, akkor a kép URL jelenik meg.

## Ismert megjegyzések

- A projekt fejlesztői környezetre készült.
- A beépített Django szerver nem éles üzemeltetésre való.
- A feltöltött képek a `media/` mappába kerülnek.


## Továbbfejlesztési lehetőségek

- kedvencek / mentett hirdetések
- kapcsolatfelvételi űrlap
- részletesebb profilkezelés
- több kép kezelése egy ingatlanhoz
- térképes megjelenítés
- kategóriák és címkék
- státusz mező (aktív / inaktív)

## Összegzés

A HomeLak projekt egy jól áttekinthető, Django alapú ingatlanhirdetési alkalmazás, amely megvalósítja az alapvető felhasználói és adminisztrációs funkciókat. A projekt alkalmas beadandó munkának, mert egyszerre mutatja be a backend logikát, az adatbázis-kezelést, az űrlapvalidációt és a felhasználói felület alapvető működését.
