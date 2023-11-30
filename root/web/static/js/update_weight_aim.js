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

function showLoading(param = true) {
  const loader = document.querySelector(".loading");
  loader.classList.remove("loading_hidden");
  loader.style.display = "flex";
  if (param) {
    document.body.style.overflow = "hidden";
  }
}

async function getWeight() {
  const request = await fetch(`../api/get_data_for_weight_aim_update_post`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id }),
  });
  const response = await request.json();
  document.querySelector("#weight_aim").value = response.weight_aim;
  return response;
}

getWeight().finally(() => {
  isFunctionsLoaded = true;
  if (isFunctionsLoaded) {
    hideLoading();
  }
});

window.onload = () => {
  if (isFunctionsLoaded) {
    hideLoading();
  }
  const button = document.querySelector(".change_link");
  button.addEventListener("click", () => {
    showLoading();
  });
};

const form = document.getElementById("form");

document
  .querySelector("form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = {};
    formData.forEach((value, key) => {
      data[key] = value;
    });
    data.tg_id = tg_id;
    try {
      const request = await fetch("../api/update_weight_aim_post", {
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
