// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBGWmVEy2zp6fpqaBkDOpV-Qj_FP6QkZj0",
  authDomain: "erudite-creek-431302-q3.firebaseapp.com",
  projectId: "erudite-creek-431302-q3",
  storageBucket: "erudite-creek-431302-q3.firebasestorage.app",
  messagingSenderId: "744217150021",
  appId: "1:744217150021:web:ec88708ad39818b87c192c",
  measurementId: "G-V3CZJNRE29"
};

// Initialize Firebase - only if the Firebase SDK is loaded
if (typeof firebase !== 'undefined') {
  firebase.initializeApp(firebaseConfig);
  
  // Initialize Analytics if available
  if (firebase.analytics) {
    const analytics = firebase.analytics();
  }
  
  console.log("Firebase inicializado correctamente");
} else {
  console.warn("Firebase SDK no está disponible");
}