import { initializeApp } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-auth.js";
import { getFirestore, doc, setDoc, getDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyCk0zvcRGwu8qLCOas-QDJnyxbs7OVyZMs",
  authDomain: "inmobiliariaremolina-b6cbe.firebaseapp.com",
  projectId: "inmobiliariaremolina-b6cbe",
  storageBucket: "inmobiliariaremolina-b6cbe.firebasestorage.app",
  messagingSenderId: "1067635512335",
  appId: "1:1067635512335:web:e604b88877dc95f5123f7a"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

const authTabs = document.querySelectorAll('.auth-tab');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginMessage = document.getElementById('login-message');
const registerMessage = document.getElementById('register-message');
const userWelcome = document.getElementById('user-welcome');
const userNameSpan = document.getElementById('user-name');
const logoutButton = document.getElementById('logout-button');
const toggleButtons = document.querySelectorAll('.toggle-password');

function showMessage(element, text, ok = false) {
  element.textContent = text;
  element.style.color = ok ? '#0b6623' : '#d8000c';
}

function switchTab(targetId) {
  authTabs.forEach(tab => {
    const target = tab.dataset.target;
    const form = document.getElementById(target);
    if (target === targetId) {
      tab.classList.add('active');
      form.classList.add('active');
      form.classList.remove('oculto');
    } else {
      tab.classList.remove('active');
      form.classList.remove('active');
      form.classList.add('oculto');
    }
  });
}

authTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    switchTab(tab.dataset.target);
    loginMessage.textContent = '';
    registerMessage.textContent = '';
  });
});

function togglePasswordInput(button) {
  const wrapper = button.parentElement;
  const input = wrapper.querySelector('input');
  if (input.type === 'password') {
    input.type = 'text';
    button.textContent = 'Ocultar';
  } else {
    input.type = 'password';
    button.textContent = 'Mostrar';
  }
}

toggleButtons.forEach(button => {
  button.addEventListener('click', () => togglePasswordInput(button));
});

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  loginMessage.textContent = '';

  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  try {
    await signInWithEmailAndPassword(auth, email, password);
    showMessage(loginMessage, 'Has iniciado sesión correctamente.', true);
  } catch (error) {
    showMessage(loginMessage, 'Error de acceso: ' + (error.message || error.code));
  }
});

registerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  registerMessage.textContent = '';

  const name = document.getElementById('register-name').value.trim();
  const email = document.getElementById('register-email').value.trim();
  const password = document.getElementById('register-password').value;

  if (password.length < 6) {
    showMessage(registerMessage, 'La contraseña debe tener al menos 6 caracteres.');
    return;
  }

  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    await setDoc(doc(db, 'usuarios', user.uid), {
      uid: user.uid,
      nombre: name,
      correo: email,
      creado: serverTimestamp()
    });
    showMessage(registerMessage, 'Cuenta creada correctamente. Ya puedes iniciar sesión.', true);
    registerForm.reset();
  } catch (error) {
    const errorCode = error.code || '';
    if (errorCode === 'auth/email-already-in-use') {
      showMessage(registerMessage, 'Este correo ya está en uso. Usa otro correo o inicia sesión.');
    } else {
      showMessage(registerMessage, 'Error al registrarse: ' + (error.message || errorCode));
    }
  }
});

logoutButton.addEventListener('click', async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error('Error al cerrar sesión:', error);
  }
});

onAuthStateChanged(auth, async (user) => {
  if (user) {
    const docRef = doc(db, 'usuarios', user.uid);
    const docSnap = await getDoc(docRef);
    const name = docSnap.exists() ? docSnap.data().nombre : user.email;
    userNameSpan.textContent = name;
    userWelcome.classList.remove('oculto');
    loginForm.classList.add('oculto');
    registerForm.classList.add('oculto');
    authTabs.forEach(tab => tab.disabled = true);
  } else {
    userWelcome.classList.add('oculto');
    loginForm.classList.remove('oculto');
    registerForm.classList.remove('oculto');
    authTabs.forEach(tab => tab.disabled = false);
    switchTab('login-form');
  }
});
