<template>
  <div class="app-container">
    <!-- 🔐 LOGIN/REGISTER SCREEN -->
    <div v-if="!isLoggedIn" class="auth-screen">
      <h1>Menadżer Haseł</h1>
      
      <div v-if="isVerifyMode">
        <h2>Potwierdź adres email</h2>
        <p>Wysłaliśmy kod na adres {{ verifyForm.email }}</p>
        <input v-model="verifyForm.code" type="text" placeholder="Kod weryfikacyjny" />
        <button @click="verifyEmail">Potwierdź</button>
        <p><small><a href="#" @click.prevent="resendVerification">Wyślij kod ponownie</a></small></p>
        <p v-if="verifyInfo" class="info">{{ verifyInfo }}</p>
        <p v-if="verifyError" class="error">{{ verifyError }}</p>
      </div>

      <div v-else-if="isForgotPasswordMode">
        <div v-if="forgotStep === 'request'">
          <h2>Zapomniałem hasła</h2>
          <input v-model="forgotForm.email" type="email" placeholder="Email" />
          <button @click="requestPasswordReset">Wyślij kod resetu</button>
        </div>
        <div v-else>
          <h2>Resetuj hasło</h2>
          <input v-model="forgotForm.code" type="text" placeholder="Kod z emaila" />
          <div class="password-field">
            <input v-model="forgotForm.newPassword" :type="showResetPassword ? 'text' : 'password'" placeholder="Nowe hasło" />
            <button type="button" class="toggle-visibility" @click="showResetPassword = !showResetPassword">{{ showResetPassword ? 'Ukryj' : 'Pokaż' }}</button>
          </div>
          <div class="password-requirements">
            <span v-for="(check, key) in resetPasswordChecks" :key="key" class="requirement" :class="{ met: check.passed }">{{ check.label }}</span>
          </div>
          <div class="password-field">
            <input v-model="forgotForm.confirmNewPassword" :type="showConfirmResetPassword ? 'text' : 'password'" placeholder="Powtórz nowe hasło" />
            <button type="button" class="toggle-visibility" @click="showConfirmResetPassword = !showConfirmResetPassword">{{ showConfirmResetPassword ? 'Ukryj' : 'Pokaż' }}</button>
          </div>
          <button @click="resetPassword">Ustaw nowe hasło</button>
        </div>
        <p><small><a href="#" @click.prevent="isForgotPasswordMode = false; forgotStep = 'request'">Wróć do logowania</a></small></p>
        <p v-if="forgotInfo" class="info">{{ forgotInfo }}</p>
        <p v-if="forgotError" class="error">{{ forgotError }}</p>
      </div>

      <div v-else-if="isRegisterMode">
        <h2>Rejestracja</h2>
        <input v-model="authForm.email" type="email" placeholder="Email" />
        <div class="password-field">
          <input v-model="authForm.password" :type="showRegisterPassword ? 'text' : 'password'" placeholder="Hasło" />
          <button type="button" class="toggle-visibility" @click="showRegisterPassword = !showRegisterPassword">{{ showRegisterPassword ? 'Ukryj' : 'Pokaż' }}</button>
        </div>
        <div class="password-requirements">
          <span v-for="(check, key) in registerPasswordChecks" :key="key" class="requirement" :class="{ met: check.passed }">{{ check.label }}</span>
        </div>
        <div class="password-field">
          <input v-model="authForm.confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" placeholder="Powtórz hasło" />
          <button type="button" class="toggle-visibility" @click="showConfirmPassword = !showConfirmPassword">{{ showConfirmPassword ? 'Ukryj' : 'Pokaż' }}</button>
        </div>
        <button @click="register">Zarejestruj się</button>
        <p><small><a href="#" @click.prevent="isRegisterMode = false">Mam już konto</a></small></p>
      </div>

      <div v-else>
        <h2>Logowanie</h2>
        <input v-model="authForm.email" type="email" placeholder="Email" />
        <div class="password-field">
          <input v-model="authForm.password" :type="showLoginPassword ? 'text' : 'password'" placeholder="Hasło" />
          <button type="button" class="toggle-visibility" @click="showLoginPassword = !showLoginPassword">{{ showLoginPassword ? 'Ukryj' : 'Pokaż' }}</button>
        </div>
        <button @click="login">Zaloguj się</button>
        <p>
          <small><a href="#" @click.prevent="isRegisterMode = true">Utwórz konto</a></small>
          &nbsp;|&nbsp;
          <small><a href="#" @click.prevent="isForgotPasswordMode = true; forgotForm.email = authForm.email">Nie pamiętasz hasła?</a></small>
        </p>
      </div>

      <p v-if="authError" class="error">{{ authError }}</p>
    </div>

    <!-- 🔑 MAIN APP (after login) -->
    <div v-else>
      <div class="header">
        <h1>Menadżer Haseł</h1>
        <button @click="logout" class="logout-btn">Wyloguj</button>
      </div>

      <!-- Klucz odszyfrowania -->
      <div class="key-section">
        <label>Klucz Fernet (do szyfrowania i odszyfrowania haseł):</label>
        <input v-model="fernetKey" type="text" placeholder="Wpisz lub wygeneruj nowy klucz Fernet" />
        <button @click="generateFernetKey" class="generate-btn">🔑 Generuj nowy klucz</button>
        <small>
          <strong>⚠️ WAŻNE:</strong> Zapisz ten klucz w bezpiecznym miejscu! Bez niego nie odszyfrujesz swoich haseł.
          Klucz jest przechowywany lokalnie w przeglądarce.
        </small>
      </div>

      <!-- Formularz dodawania -->
      <div class="form-section">
        <input v-model="newPassword.service" type="text" placeholder="Serwis" />
        <input v-model="newPassword.login" type="text" placeholder="Login" />
        <input v-model="newPassword.password" type="password" placeholder="Hasło" />
        <button @click="addPassword">Dodaj</button>
      </div>

      <!-- Lista haseł -->
      <ul>
        <li v-for="item in passwords" :key="item.id">
          <strong>{{ item.service }}</strong> – {{ item.login }} – 
          <span>{{ decrypted[item.id] || "***" }}</span>

          <button @click="togglePasswordVisibility(item.id, item.password)">
            {{ decrypted[item.id] ? 'Ukryj' : 'Pokaż' }}
          </button>
          <button @click="deletePassword(item.id)" class="delete-btn">Usuń</button>
        </li>
      </ul>

      <p v-if="passwords.length === 0" class="no-passwords">Brak zapisanych haseł</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

// Backend na tym samym hoście
const API_URL = window.location.origin;
axios.defaults.withCredentials = true;

export default {
  data() {
    return {
      isLoggedIn: false,
      isRegisterMode: false,
      authForm: { email: "", password: "", confirmPassword: "" },
      authError: "",
      passwords: [],
      decrypted: {},
      newPassword: { service: "", login: "", password: "" },
      fernetKey: "",
      currentUserEmail: "",

      showLoginPassword: false,
      showRegisterPassword: false,
      showConfirmPassword: false,

      isVerifyMode: false,
      verifyForm: { email: "", code: "" },
      verifyError: "",
      verifyInfo: "",

      isForgotPasswordMode: false,
      forgotStep: "request",
      forgotForm: { email: "", code: "", newPassword: "", confirmNewPassword: "" },
      forgotError: "",
      forgotInfo: "",
      showResetPassword: false,
      showConfirmResetPassword: false,
    };
  },
  computed: {
    registerPasswordChecks() {
      return this.getPasswordChecks(this.authForm.password);
    },
    registerPasswordValid() {
      return Object.values(this.registerPasswordChecks).every((c) => c.passed);
    },
    resetPasswordChecks() {
      return this.getPasswordChecks(this.forgotForm.newPassword);
    },
    resetPasswordValid() {
      return Object.values(this.resetPasswordChecks).every((c) => c.passed);
    },
  },
  methods: {
    getPasswordChecks(password) {
      return {
        length: { label: "Min. 8 znaków", passed: password.length >= 8 },
        lower: { label: "Mała litera", passed: /[a-z]/.test(password) },
        upper: { label: "Wielka litera", passed: /[A-Z]/.test(password) },
        digit: { label: "Cyfra", passed: /[0-9]/.test(password) },
        special: { label: "Znak specjalny", passed: /[^a-zA-Z0-9]/.test(password) },
      };
    },
    async register() {
      this.authError = "";
      if (!this.registerPasswordValid) {
        this.authError = "Hasło nie spełnia wymagań bezpieczeństwa";
        return;
      }
      if (this.authForm.password !== this.authForm.confirmPassword) {
        this.authError = "Hasła nie są identyczne";
        return;
      }
      try {
        const res = await axios.post(`${API_URL}/auth/register`, {
          email: this.authForm.email,
          password: this.authForm.password,
        });
        this.authError = "";
        this.isRegisterMode = false;
        // Nowe konto - pole klucza pozostaje puste
        this.fernetKey = "";
        // Przejdź do ekranu wpisania kodu weryfikacyjnego
        this.verifyForm = { email: this.authForm.email, code: "" };
        this.verifyError = "";
        this.verifyInfo = "";
        this.isVerifyMode = true;
      } catch (err) {
        this.authError = err.response?.data?.detail || "Błąd rejestracji";
      }
    },
    async login() {
      try {
        const email = this.authForm.email;
        await axios.post(`${API_URL}/auth/login`, {
          email: email,
          password: this.authForm.password,
        });
        this.isLoggedIn = true;
        this.authError = "";
        this.currentUserEmail = email;
        this.authForm = { email: "", password: "", confirmPassword: "" };
        // Wczytaj klucz dla tego użytkownika z localStorage
        this.fernetKey = localStorage.getItem(`fernetKey_${this.currentUserEmail}`) || "";
        this.fetchPasswords();
      } catch (err) {
        if (err.response?.status === 403) {
          // Konto niezweryfikowane - przejdź do ekranu wpisania kodu
          this.verifyForm = { email: this.authForm.email, code: "" };
          this.verifyError = "";
          this.verifyInfo = "";
          this.isVerifyMode = true;
        } else {
          this.authError = err.response?.data?.detail || "Błędne dane logowania";
        }
      }
    },
    async verifyEmail() {
      try {
        await axios.post(`${API_URL}/auth/verify-email`, {
          email: this.verifyForm.email,
          code: this.verifyForm.code,
        });
        this.verifyError = "";
        this.isVerifyMode = false;
        alert("Email potwierdzony! Zaloguj się.");
      } catch (err) {
        this.verifyError = err.response?.data?.detail || "Błąd weryfikacji kodu";
      }
    },
    async resendVerification() {
      try {
        await axios.post(`${API_URL}/auth/resend-verification`, {
          email: this.verifyForm.email,
        });
        this.verifyError = "";
        this.verifyInfo = "Kod wysłany ponownie";
      } catch (err) {
        this.verifyError = err.response?.data?.detail || "Błąd wysyłania kodu";
      }
    },
    async requestPasswordReset() {
      try {
        await axios.post(`${API_URL}/auth/forgot-password`, {
          email: this.forgotForm.email,
        });
        this.forgotError = "";
        this.forgotInfo = "Jeśli konto istnieje, wysłaliśmy kod resetu";
        this.forgotStep = "reset";
      } catch (err) {
        this.forgotError = err.response?.data?.detail || "Błąd wysyłania kodu";
      }
    },
    async resetPassword() {
      this.forgotError = "";
      if (!this.resetPasswordValid) {
        this.forgotError = "Hasło nie spełnia wymagań bezpieczeństwa";
        return;
      }
      if (this.forgotForm.newPassword !== this.forgotForm.confirmNewPassword) {
        this.forgotError = "Hasła nie są identyczne";
        return;
      }
      try {
        await axios.post(`${API_URL}/auth/reset-password`, {
          email: this.forgotForm.email,
          code: this.forgotForm.code,
          new_password: this.forgotForm.newPassword,
        });
        this.forgotError = "";
        this.isForgotPasswordMode = false;
        this.forgotStep = "request";
        this.forgotForm = { email: "", code: "", newPassword: "", confirmNewPassword: "" };
        alert("Hasło zmienione! Zaloguj się nowym hasłem.");
      } catch (err) {
        this.forgotError = err.response?.data?.detail || "Błąd resetowania hasła";
      }
    },
    async logout() {
      try {
        await axios.post(`${API_URL}/auth/logout`);
      } catch (err) {
        console.error("Błąd wylogowania:", err);
      }
      this.isLoggedIn = false;
      this.passwords = [];
      this.decrypted = {};
      // Wyczyść klucz z pamięci (ale zostaw w localStorage dla tego konta)
      this.fernetKey = "";
      this.currentUserEmail = "";
    },
    async fetchPasswords() {
      try {
        const res = await axios.get(`${API_URL}/passwords`);
        this.passwords = res.data;
      } catch (err) {
        console.error("Błąd pobierania haseł:", err);
      }
    },
    async addPassword() {
      if (!this.fernetKey || this.fernetKey.trim() === "") {
        alert("Najpierw wpisz lub wygeneruj klucz Fernet!");
        return;
      }
      console.log("[ADD] Klucz używany:", this.fernetKey);
      console.log("[ADD] Długość klucza:", this.fernetKey.length);
      console.log("[ADD] Hasło:", this.newPassword.password);
      try {
        const response = await axios.post(`${API_URL}/passwords`, {
          ...this.newPassword,
          key: this.fernetKey.trim()
        });
        console.log("[ADD] Response:", response.data);
        console.log("[ADD] Zaszyfrowane hasło:", response.data.password);
        this.newPassword = { service: "", login: "", password: "" };
        this.fetchPasswords();
      } catch (err) {
        console.error("[ADD] BŁĄD:", err);
        alert(err.response?.data?.detail || "Błąd dodawania hasła");
      }
    },
    async deletePassword(id) {
      if (confirm("Na pewno usunąć hasło?")) {
        try {
          await axios.delete(`${API_URL}/passwords/${id}`);
          this.fetchPasswords();
        } catch (err) {
          alert("Błąd usuwania");
        }
      }
    },
    togglePasswordVisibility(id, encrypted) {
      // Jeśli hasło jest już widoczne - ukryj je
      if (this.decrypted[id]) {
        delete this.decrypted[id];
        return;
      }
      // W przeciwnym razie - odszyfruj i pokaż
      this.decryptPassword(id, encrypted);
    },
    async decryptPassword(id, encrypted) {
      if (!this.fernetKey || this.fernetKey.trim() === "") {
        alert("Najpierw wpisz klucz Fernet!");
        return;
      }
      console.log("[DECRYPT] ID:", id);
      console.log("[DECRYPT] Klucz używany:", this.fernetKey);
      console.log("[DECRYPT] Długość klucza:", this.fernetKey.length);
      console.log("[DECRYPT] Zaszyfrowane hasło:", encrypted);
      console.log("[DECRYPT] Długość zaszyfrowanego:", encrypted.length);
      try {
        const res = await axios.post(
          `${API_URL}/passwords/decrypt`,
          { key: this.fernetKey.trim(), password: encrypted }
        );
        console.log("[DECRYPT] Response:", res.data);
        console.log("[DECRYPT] Odszyfrowane hasło:", res.data.decrypted);
        // Vue 3: nie używamy $set - reaktywność działa automatycznie
        this.decrypted[id] = res.data.decrypted;
      } catch (err) {
        console.error("[DECRYPT] BŁĄD:", err);
        console.error("[DECRYPT] Response data:", err.response?.data);
        alert(err.response?.data?.detail || "Błąd odszyfrowania - sprawdź czy klucz jest poprawny");
      }
    },
    generateFernetKey() {
      // Generuj 32 losowe bajty
      const array = new Uint8Array(32);
      crypto.getRandomValues(array);
      
      console.log("[GEN] Losowe bajty (hex):", Array.from(array).map(b => b.toString(16).padStart(2, '0')).join(''));
      
      // Konwertuj do base64 (poprawnie obsługując wszystkie bajty)
      let binary = '';
      for (let i = 0; i < array.length; i++) {
        binary += String.fromCharCode(array[i]);
      }
      const base64 = btoa(binary);
      
      console.log("[GEN] Klucz base64:", base64);
      console.log("[GEN] Długość klucza:", base64.length);
      
      this.fernetKey = base64;
      // Zapisz klucz dla tego konkretnego użytkownika
      console.log("[GEN] Email użytkownika:", this.currentUserEmail);
      console.log("[GEN] Zapisuję klucz jako:", `fernetKey_${this.currentUserEmail}`);
      if (this.currentUserEmail) {
        localStorage.setItem(`fernetKey_${this.currentUserEmail}`, base64);
        console.log("[GEN] Klucz zapisany w localStorage");
      } else {
        console.error("[GEN] BRAK EMAIL - klucz NIE został zapisany!");
      }
      alert("✅ Klucz wygenerowany!\n\n⚠️ ZAPISZ GO W BEZPIECZNYM MIEJSCU!\n\nBez tego klucza nie odszyfrujesz swoich haseł.\n\nKlucz: " + base64);
    },
  },
  watch: {
    fernetKey(newKey) {
      // Zapisuj klucz dla konkretnego użytkownika
      if (newKey && this.currentUserEmail) {
        localStorage.setItem(`fernetKey_${this.currentUserEmail}`, newKey);
      }
    },
  },
  mounted() {
    axios
      .get(`${API_URL}/auth/me`)
      .then((response) => {
        this.isLoggedIn = true;
        // Pobierz email z odpowiedzi (zakładam, że endpoint /auth/me zwraca dane użytkownika)
        console.log("[MOUNTED] Response /auth/me:", response.data);
        this.currentUserEmail = response.data.email;
        console.log("[MOUNTED] Email:", this.currentUserEmail);
        // Wczytaj klucz dla tego użytkownika
        this.fernetKey = localStorage.getItem(`fernetKey_${this.currentUserEmail}`) || "";
        console.log("[MOUNTED] Wczytany klucz:", this.fernetKey);
        this.fetchPasswords();
      })
      .catch(() => {
        this.isLoggedIn = false;
      });
  },
};
</script>

<style>
body {
  background-color: #f5f5f5;
  color: #333;
  font-family: Arial, sans-serif;
  margin: 0;
}

.app-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.auth-screen {
  text-align: center;
}

.auth-screen h1 {
  color: #0066cc;
}

.auth-screen h2 {
  color: #333;
  margin: 20px 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.logout-btn {
  background: #ff4444;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background: #cc0000;
}

.key-section {
  margin: 20px 0;
  padding: 15px;
  background: #fff9e6;
  border: 2px solid #ffd700;
  border-radius: 8px;
}

.key-section label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.key-section input {
  font-family: monospace;
  font-size: 14px;
  margin-bottom: 8px;
}

.key-section small {
  display: block;
  color: #666;
  margin-top: 5px;
}

.key-section code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  color: #d63384;
}

.generate-btn {
  background: #28a745;
  margin-top: 10px;
}

.generate-btn:hover {
  background: #218838;
}

input, button {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
}

input {
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  color: #000;
}

input:focus {
  outline: none;
  border-color: #0066cc;
}

button {
  background: #0066cc;
  color: white;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

button:hover {
  background: #0052a3;
}

.form-section {
  margin: 20px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.form-section input {
  margin: 8px 0;
}

.form-section button {
  margin-top: 10px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  background: #f5f5f5;
  padding: 12px;
  margin: 8px 0;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

li strong {
  color: #0066cc;
}

li button {
  display: inline-block;
  width: auto;
  padding: 6px 12px;
  margin: 0 4px;
  font-size: 12px;
}

.delete-btn {
  background: #ff6666;
}

.delete-btn:hover {
  background: #ff4444;
}

.error {
  color: #ff0000;
  margin: 10px 0;
}

.info {
  color: #28a745;
  margin: 10px 0;
}

.password-field {
  display: flex;
  gap: 8px;
  margin: 10px 0;
}

.password-field input {
  flex: 1;
  margin: 0;
}

.password-field .toggle-visibility {
  display: block;
  width: auto;
  margin: 0;
  padding: 12px 14px;
  white-space: nowrap;
}

.password-requirements {
  text-align: left;
  margin: 4px 0 10px;
}

.requirement {
  display: inline-block;
  padding: 4px 8px;
  margin: 3px 4px 3px 0;
  border-radius: 12px;
  font-size: 12px;
  background: #eee;
  color: #777;
}

.requirement.met {
  background: #28a745;
  color: white;
}

.no-passwords {
  text-align: center;
  color: #999;
  padding: 20px;
}

a {
  color: #0066cc;
  text-decoration: none;
  cursor: pointer;
}

a:hover {
  text-decoration: underline;
}
</style>
