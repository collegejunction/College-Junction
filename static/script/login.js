function showForm(formType) {
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const loginTab = document.getElementById("login-tab");
    const signupTab = document.getElementById("signup-tab");
  
    if (formType === "login") {
      loginForm.classList.add("active");
      signupForm.classList.remove("active");
      loginTab.classList.add("active");
      signupTab.classList.remove("active");
    } else {
      signupForm.classList.add("active");
      loginForm.classList.remove("active");
      signupTab.classList.add("active");
      loginTab.classList.remove("active");
    }
  }
  