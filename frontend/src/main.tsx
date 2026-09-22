import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles.css";
import "./fsdp.css";
import "./fsdp-polish.css";
import "./faculty-pages.css";
import "./maintenance.css";
import "./grant-review.css";
import "./print.css";

createRoot(document.getElementById("root")!).render(<StrictMode><BrowserRouter><App /></BrowserRouter></StrictMode>);
