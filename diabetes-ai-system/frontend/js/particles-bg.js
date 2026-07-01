// Animated particle background using tsParticles, themed as floating medical
// data points (cyan dots, soft connecting lines).
const ParticlesBg = {
  async init() {
    if (typeof tsParticles === "undefined") return;
    await tsParticles.load({
      id: "particles-bg",
      options: {
        fullScreen: { enable: false },
        background: { color: { value: "transparent" } },
        fpsLimit: 60,
        particles: {
          number: { value: 60, density: { enable: true, area: 900 } },
          color: { value: ["#00E5FF", "#7B5CFF"] },
          shape: { type: "circle" },
          opacity: { value: 0.45, random: true },
          size: { value: { min: 1, max: 2.6 } },
          links: {
            enable: true,
            distance: 140,
            color: "#00E5FF",
            opacity: 0.12,
            width: 1,
          },
          move: {
            enable: true,
            speed: 0.5,
            direction: "none",
            random: true,
            outModes: { default: "out" },
          },
        },
        interactivity: {
          events: {
            onHover: { enable: true, mode: "grab" },
          },
          modes: {
            grab: { distance: 140, links: { opacity: 0.3 } },
          },
        },
        detectRetina: true,
      },
    });
  },
};
