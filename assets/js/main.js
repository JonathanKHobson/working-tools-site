import { startCatalog } from "./catalog.js?v=phase3-release-history-1";
import { startNavigation } from "./site-nav.js";

document.documentElement.classList.add("js-enabled");

startNavigation();
startCatalog();
