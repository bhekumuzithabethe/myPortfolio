function toggleTheme() {
  const html = document.documentElement;
  const icon = document.getElementById("theme-icon");
  const currentTheme = html.getAttribute("data-bs-theme") || "light";
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  html.setAttribute("data-bs-theme", newTheme);
  localStorage.setItem("preferred-theme", newTheme);

  // Switch icon
  if (newTheme === "dark") {
    icon.classList.add("fa-sun");
    icon.classList.remove("fa-moon");
  } else {
    icon.classList.add("fa-moon");
    icon.classList.remove("fa-sun");
  }
}

// Load saved theme and icon on page load
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("preferred-theme") || "light";
  document.documentElement.setAttribute("data-bs-theme", savedTheme);

  const icon = document.getElementById("theme-icon");
  if (savedTheme === "dark") {
    icon.classList.add("fa-sun");
    icon.classList.remove("fa-moon");
  } else {
    icon.classList.add("fa-moon");
    icon.classList.remove("fa-sun");
  }
});