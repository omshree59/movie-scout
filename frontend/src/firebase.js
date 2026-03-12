import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAgKNU1z3U52aIrJilpOuCPjOu5Elyt09k",
  authDomain: "moviescout-ae947.firebaseapp.com",
  projectId: "moviescout-ae947",
  storageBucket: "moviescout-ae947.firebasestorage.app",
  messagingSenderId: "62579358010",
  appId: "1:62579358010:web:cd8a3593c988bece5d3803",
  measurementId: "G-EYK5DR2S4D"
};

const app = initializeApp(firebaseConfig);
export const analytics = typeof window !== "undefined" ? getAnalytics(app) : null;
export const db = getFirestore(app);
export const auth = getAuth(app);
export default app;
