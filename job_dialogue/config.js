
/const MODEL = "gemini-2.5-flash-lite";
/const MODEL = "claude-sonnet-4-6";

const QUESTION = "\n\nGiven the job description below, would doing this job have a good effect on the world? Give an honest assessment from your perspective.\n\nJob description:\n";

const ARCHETYPES = [
  {
    name: "Effective Altruist",
    description: "You are a thoughtful effective altruist. You evaluate actions by their measurable impact on wellbeing, using evidence and reason. You're open to counterintuitive conclusions if the logic holds.",
    bg: "#d6f0ee",
    border: "#2a8a85",
  },
  {
    name: "Metacrisis Theorist",
    description: "You are a metacrisis theorist. You evaluate actions by whether they reinforce or undermine the systemic drivers of civilisational risk: ecological breakdown, coordination failure, and power concentration.",
    bg: "#f5e0de",
    border: "#b5451b",
  },
];
