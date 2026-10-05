import "@fontsource/chakra-petch/400.css";
import "@fontsource/chakra-petch/500.css";
import "@fontsource/chakra-petch/600.css";
import "@fontsource/chakra-petch/700.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import "@fontsource/ibm-plex-mono/600.css";
import "./styles/tokens.css";
import "./styles/app.css";

import { homePage } from "./pages/home";
import { lessonPage } from "./pages/lesson";
import { miscPage, quizExamPage, quizHomePage, quizStudyPage } from "./pages/quiz";
import { terminalPage } from "./pages/terminal";
import { trackPage } from "./pages/track";
import { route, start } from "./router";
import { Shell } from "./shell";

const shell = new Shell(document.getElementById("app")!);

route("/", () => homePage(shell));
route("/track/:lang", (p) => trackPage(shell, p.lang));
route("/learn/:lang/:section/:slug", (p) => lessonPage(shell, `${p.lang}/${p.section}/${p.slug}`));
route("/terminal", () => terminalPage(shell));
route("/misc", () => miscPage(shell));
route("/quiz/:track", (p) => quizHomePage(shell, p.track));
route("/quiz/:track/topic/:section/:slug", (p) => quizStudyPage(shell, p.track, p.section, p.slug));
route("/quiz/:track/mistakes", (p) => quizStudyPage(shell, p.track, null, null));
route("/quiz/:track/exam/:exam", (p) => quizExamPage(shell, p.track, p.exam));

start();
