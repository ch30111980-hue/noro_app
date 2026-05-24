# NORO — Administration Digitale IA
## Guide de déploiement complet

---

## 📁 Structure du projet

```
noro_app/
├── app.py              ← Application Flask principale
├── requirements.txt    ← Dépendances Python
├── users.json          ← Base utilisateurs (auto-créé au 1er lancement)
├── templates/
│   ├── login.html      ← Page de connexion NORO
│   └── dashboard.html  ← Tableau de bord
└── static/             ← CSS / images (optionnel)
```

---

## 🚀 Installation rapide (5 étapes)

### 1. Installer Python
Télécharge Python 3.10+ sur https://python.org

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer en local (test)
```bash
python app.py
```
→ Ouvre http://127.0.0.1:5000 dans ton navigateur

### 4. Compte par défaut
```
Email    : admin@noro.dz
Password : noro2026
```
⚠️ Change le mot de passe dès la première connexion !

---

## 🌐 Déploiement en production (serveur VPS)

### Option A — Gunicorn (Linux)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option B — Render.com (gratuit)
1. Crée un compte sur https://render.com
2. Nouveau projet → Web Service → connecte ton GitHub
3. Build command : `pip install -r requirements.txt`
4. Start command : `gunicorn app:app`
5. Ton site sera disponible sur `https://noro.onrender.com`

### Option C — PythonAnywhere (gratuit)
1. Crée un compte sur https://www.pythonanywhere.com
2. Upload les fichiers dans `/home/tonnom/noro_app/`
3. Onglet Web → Add new web app → Flask
4. WSGI file : pointe vers `app.py`

---

## 🔐 API disponibles

| Méthode | Route           | Description                        |
|---------|----------------|------------------------------------|
| POST    | /login          | Connexion (formulaire HTML)        |
| GET     | /logout         | Déconnexion                        |
| GET     | /dashboard      | Tableau de bord (protégé)          |
| POST    | /api/login      | Connexion JSON (fetch/mobile)      |
| GET     | /api/status     | Vérifier si connecté               |
| GET     | /api/users      | Liste utilisateurs (admin only)    |
| POST    | /api/users/add  | Ajouter un utilisateur (admin only)|

### Exemple d'appel API (JavaScript fetch)
```javascript
const response = await fetch('/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'admin@noro.dz', password: 'noro2026' })
});
const data = await response.json();
console.log(data); // { success: true, nom: "Administrateur NORO", role: "admin" }
```

### Ajouter un utilisateur via API
```javascript
await fetch('/api/users/add', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'ingenieur@noro.dz',
    password: 'monmotdepasse',
    nom: 'Ahmed Benali',
    role: 'user',
    secteur: 'Génie Civil'
  })
});
```

---

## ⚙️ Variables d'environnement

Crée un fichier `.env` à la racine :
```
NORO_SECRET=une-cle-secrete-tres-longue-et-unique
```

---

## 🔧 Personnalisation

- **Ajouter une vraie base de données** → Remplace `users.json` par SQLAlchemy + PostgreSQL
- **Envoyer des emails** → Installe Flask-Mail
- **HTTPS** → Configure avec Nginx + Certbot (Let's Encrypt)
- **Domaine personnalisé** → ex: www.noro.dz

---

© 2026 NORO — Administration Digitale IA — Algeria, DZ
