import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#202124",
        moss: "#2f5d50",
        clay: "#a05a3b",
        mist: "#eef4f1",
      },
    },
  },
  plugins: [],
};

export default config;
