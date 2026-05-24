"""
NORO — Administration Digitale IA
Application Flask principale
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import hashlib, os, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("NORO_SECRET", "noro-secret-change-this-in-production-2026")

# ─────────────────────────────────────────
#  BASE DE DONNÉES UTILISATEURS (JSON simple)
#  → Remplace par PostgreSQL / MySQL en prod
# ─────────────────────────────────────────
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    # Utilisateur admin par défaut
    default = {
        "admin@noro.dz": {
            "password": hash_password("noro2026"),
            "nom": "Administrateur NORO",
            "role": "admin",
            "secteur": "Tous",
            "created": datetime.now().isoformat()
        }
    }
    save_users(default)
    return default

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# ─────────────────────────────────────────
#  DÉCORATEUR : PROTECTION DES ROUTES
# ─────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    """Page d'accueil → redirige vers login ou dashboard"""
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion NORO"""
    if "user_email" in session:
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember")

        users = load_users()

        if email in users and users[email]["password"] == hash_password(password):
            session["user_email"] = email
            session["user_nom"]   = users[email]["nom"]
            session["user_role"]  = users[email]["role"]
            if remember:
                app.permanent_session_lifetime = __import__("datetime").timedelta(days=30)
                session.permanent = True
            return redirect(url_for("dashboard"))
        else:
            error = "Identifiant ou mot de passe incorrect."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Tableau de bord principal (à personnaliser)"""
    noro_unified_url = os.environ.get("NORO_UNIFIED_URL", "http://127.0.0.1:5002/")
    return render_template("dashboard.html",
        nom=session.get("user_nom", "Utilisateur"),
        role=session.get("user_role", "user"),
        email=session.get("user_email"),
        noro_unified_url=noro_unified_url
    )


# ─── API JSON ───────────────────────────

@app.route("/api/login", methods=["POST"])
def api_login():
    """Connexion via API (pour apps mobiles ou fetch JS)"""
    data     = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    users = load_users()
    if email in users and users[email]["password"] == hash_password(password):
        session["user_email"] = email
        session["user_nom"]   = users[email]["nom"]
        session["user_role"]  = users[email]["role"]
        return jsonify({"success": True, "nom": users[email]["nom"], "role": users[email]["role"]})
    return jsonify({"success": False, "message": "Identifiant ou mot de passe incorrect"}), 401


@app.route("/api/status")
def api_status():
    """Vérifier si l'utilisateur est connecté"""
    if "user_email" in session:
        return jsonify({
            "logged_in": True,
            "email": session["user_email"],
            "nom": session["user_nom"],
            "role": session["user_role"]
        })
    return jsonify({"logged_in": False})


@app.route("/api/users", methods=["GET"])
@login_required
def api_users():
    """Liste des utilisateurs (admin uniquement)"""
    if session.get("user_role") != "admin":
        return jsonify({"error": "Accès refusé"}), 403
    users = load_users()
    # Ne jamais renvoyer les mots de passe
    safe = {email: {k: v for k, v in info.items() if k != "password"}
            for email, info in users.items()}
    return jsonify(safe)


@app.route("/api/users/add", methods=["POST"])
@login_required
def api_add_user():
    """Ajouter un utilisateur (admin uniquement)"""
    if session.get("user_role") != "admin":
        return jsonify({"error": "Accès refusé"}), 403

    data = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")
    nom      = data.get("nom", "Nouvel utilisateur")
    role     = data.get("role", "user")
    secteur  = data.get("secteur", "Génie Civil")

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    users = load_users()
    if email in users:
        return jsonify({"error": "Utilisateur déjà existant"}), 409

    users[email] = {
        "password": hash_password(password),
        "nom": nom,
        "role": role,
        "secteur": secteur,
        "created": datetime.now().isoformat()
    }
    save_users(users)
    return jsonify({"success": True, "message": f"Utilisateur {email} créé avec succès"})


# ─────────────────────────────────────────
#  LANCEMENT
# ─────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print("=" * 50)
    print("  NORO — Administration Digitale IA")
    print(f"  http://127.0.0.1:{port}")
    print("  Compte par défaut : admin@noro.dz / noro2026")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=port)
