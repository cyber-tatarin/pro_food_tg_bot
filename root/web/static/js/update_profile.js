const tg = window.Telegram.WebApp;
const tg_id = tg.initDataUnsafe.user.id;

let isFunctionsLoaded = false;

function hideLoading() {
  const loader = document.querySelector(".loading");
  loader.classList.add("loading_hidden");
  loader.addEventListener("transitionend", function () {
    loader.style.display = "none";
  });
  document.body.style.overflow = "visible";
}

async function getDate() {
  const request = await fetch(`../api/get_data_for_profile_update_post`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id }),
  });
  const response = await request.json();
  document.querySelector("#height").value = response.height;
  document.querySelector("#date").value = response.birth_date;
  return response;
}

getDate().finally(() => {
  isFunctionsLoaded = true;
  if (isFunctionsLoaded) {
    hideLoading();
  }
});

window.onload = () => {
  if (isFunctionsLoaded) {
    hideLoading();
  }
};

const form = document.getElementById("form");

form.addEventListener("submit", async function (event) {
  event.preventDefault();

  const formData = new FormData(event.target);
  const data = {};

  formData.forEach((value, key) => {
    if (key === "date" && value) {
      const splitDate = value.split("-");
      data[key] = `${splitDate[2]}-${splitDate[1]}-${splitDate[0]}`;
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
