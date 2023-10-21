let choicesCounter = 1;
let tg = window.Telegram.WebApp;
const tg_id = 459471362 || tg.initDataUnsafe.user.id;

const elements = document.querySelectorAll(`.js-choice_type`);
elements.forEach((el) => {
  const choices = new Choices(el, {
    itemSelectText: "",
    noResultsText: "Не найдено",
  });
  el.addEventListener(
    "choice",
    function (event) {
      el.parentElement.style.color = "#303030";
    },
    false
  );
});

const renderSelect = (response, data) => {
  const elements = document.querySelectorAll(`.js-choice_${choicesCounter++}`);
  elements.forEach((el) => {
    const choices = new Choices(el, {
      itemSelectText: "",
      noResultsText: "Не найдено",
    });
    el.addEventListener(
      "choice",
      function (event) {
        el.parentElement.style.color = "#303030";
      },
      false
    );
    choices.setChoices(data, "value", "label", false);
  });
};

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
  isImagesLoaded = true;
  if (isFunctionsLoaded) {
    hideLoading();
  }
};

getData().finally(() => {
  isFunctionsLoaded = true;
  if (isImagesLoaded) {
    hideLoading();
  }
});

let testChoices = [];
let response;

const form = document.getElementById("form");

document
  .querySelector("form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const checkboxes = document.querySelectorAll(".step_radio");

    let selectedCheckboxValue = null;
    for (const checkbox of checkboxes) {
      if (checkbox.checked) {
        selectedCheckboxValue = checkbox.id;
        break;
      }
    }

    const formData = new FormData(event.target);
    const data = {};
    let selectedCheckbox;
    formData.forEach((value, key) => {
      if (key !== "next_step") {
        data[key] = value;
      } else {
        selectedCheckbox = value;
      }
    });
    data.tg_id = tg_id;
    try {
      const request = await fetch("../api/add_ingredient", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const response = await request.json();
      if (response.success === true) {
        const stepInputs = document.querySelectorAll(".step_radio");
        stepInputs.forEach((step) => {
          if (step.checked) {
            if (step.id === "close") {
              let tg = window.Telegram.WebApp;
              tg.close();
            } else if (step.id === "add-ingredient") {
              window.location.href = "../add_ingredient";
            } else if (step.id === "add-dish") {
              window.location.href = "../add_meal";
            } else {
              window.location.href = "../add_plate";
            }
          }
        });
        document.querySelector(".error").classList.remove("error_active");
      } else {
        document.querySelector(".error").classList.add("error_active");
        document.querySelector(".error").textContent = response.error_message;
      }
    } catch (err) {
      console.log(err);
    }
  });

async function getData() {
  try {
    const request = await fetch("../api/get_ingredients_list", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    response = await request.json();

    testChoices = response.map((item) => ({
      value: item.measure,
      label: "Мера",
    }));
    renderSelect(response, testChoices);

    return response;
  } catch (error) {
    console.error("Ошибка при получении данных:", error);
  }
}
