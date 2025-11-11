

  import { createRoot } from "react-dom/client";
  import App from "./App.tsx";
  import "./index.css";

  // Remove any injected divs that might cause layout issues
  const cleanupInjectedElements = () => {
    const bodyChildren = Array.from(document.body.children);
    bodyChildren.forEach((child) => {
      // Remove elements that are not the root div
      if (child.id !== 'root' && child instanceof HTMLDivElement) {
        // Check if it's an empty div or has shadowRoot (likely from extensions)
        if (!child.className || child.shadowRoot) {
          child.style.display = 'none';
          child.style.position = 'absolute';
          child.style.width = '0';
          child.style.height = '0';
          child.style.overflow = 'hidden';
          child.style.visibility = 'hidden';
        }
      }
    });
  };

  // Run cleanup on load
  cleanupInjectedElements();

  // Also run after a short delay to catch late injections
  setTimeout(cleanupInjectedElements, 100);
  setTimeout(cleanupInjectedElements, 500);

  // Watch for new elements being added
  const observer = new MutationObserver(cleanupInjectedElements);
  observer.observe(document.body, { childList: true });

  createRoot(document.getElementById("root")!).render(<App />);
  
  