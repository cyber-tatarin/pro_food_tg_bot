let choicesCounter = 1;
const tg = window.Telegram.WebApp;
const tg_id = tg.initDataUnsafe.user.id;

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
};

const form = document.getElementById("form");

form.addEventListener("submit", async function (event) {
  event.preventDefault();
  console.log("submit");

  const formData = new FormData(event.target);
  const data = {};

  // Изменение формата даты перед добавлением в объект данных
  formData.forEach((value, key) => {
    if (key === "date" && value) {
      // Проверяем, что это поле с датой и оно не пустое
      const splitDate = value.split("-"); // yyyy-mm-dd
      data[key] = `${splitDate[2]}-${splitDate[1]}-${splitDate[0]}`; // dd-mm-yyyy
    } else {
      data[key] = value;
    }
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
