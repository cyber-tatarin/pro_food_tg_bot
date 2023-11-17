let choicesCounter = 1;
const tg = window.Telegram.WebApp;
const tg_id = 459471362; // Заменено на конкретный ID для демонстрации

let isFunctionsLoaded = false;
let isImagesLoaded = false;

function hideLoading() {
  const loader = document.querySelector(".loading");
  loader.classList.add("loading_hidden");
  loader.addEventListener("transitionend", function () {
    loader.style.display = "none";
  });
  document.body.style.overflow = "visible";
}

window.onload = () => {
  hideLoading();

  // Инициализация Flatpickr
  var dateButton = document.getElementById("dateButton");
  var hiddenDateInput = document.getElementById("hiddenDateInput");

  flatpickr(dateButton, {
    dateFormat: "d.m.Y",
    onChange: function (selectedDates, dateStr) {
      document.querySelector("#dateButton").classList.remove("calendar_grey");
      document.querySelector(".error").classList.remove("error_active");
      hiddenDateInput.value = dateStr;
      dateButton.textContent = selectedDates[0].toLocaleDateString("ru");
    },
  });
};

const form = document.getElementById("form");

form.addEventListener("submit", async function (event) {
  event.preventDefault();
  if (!hiddenDateInput.value) {
    document.querySelector(".error").classList.add("error_active");
    document.querySelector(".error").textContent = "Пожалуйста, введите дату";
    return;
  }

  console.log("submit");
  const formData = new FormData(event.target);
  const data = {};
  formData.forEach((value, key) => {
    data[key] = value;
  });
  data.tg_id = tg_id;

  try {
    const request = await fetch("../api/update_profile_post", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const response = await request.json();

    if (response.success === true) {
      document.querySelector(".error").classList.remove("error_active");
      window.location.href = "../main";
    } else {
      document.querySelector(".error").classList.add("error_active");
      document.querySelector(".error").textContent = response.error_message;
    }
  } catch (err) {
    console.log(err);
  }
});
