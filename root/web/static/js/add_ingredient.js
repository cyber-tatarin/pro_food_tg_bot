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
        console.log("label", event.detail.choice.label);
        console.log("value", event.detail.choice.value);
        el.parentElement.style.color = "#303030";
      },
      false
    );
    console.log(data);
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
  console.log("successfully");
  isImagesLoaded = true;
  if (isFunctionsLoaded) {
    hideLoading();
  }
};

getData().finally(() => {
  console.log("finally");
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

    console.log(selectedCheckboxValue);
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
      console.log(response);
      if (response.success === true) {
        console.log("redirect");
        const stepInputs = document.querySelectorAll(".step_radio");
        stepInputs.forEach((step) => {
          if (step.checked) {
            if (step.id === "close") {
              console.log("close");
              let tg = window.Telegram.WebApp;
              tg.close();
            } else if (step.id === "add-ingredient") {
              window.location.href = "../add_ingredient";
              console.log("add-ingredient");
            } else if (step.id === "add-dish") {
              window.location.href = "../add_meal";
              console.log("add-dish");
            } else {
              window.location.href = "../add_plate";
              console.log("else");
            }
          }
        });
        document.querySelector(".error").classList.remove("error_active");
      } else {
        document.querySelector(".error").classList.add("error_active");
        document.querySelector(".error").textContent = response.error_message;
        console.log(response);
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
    console.log("response", response, choicesCounter);

    testChoices = response.map((item) => ({
      value: item.measure,
      label: "Мера",
    }));
    console.log(testChoices);
    renderSelect(response, testChoices);

    return response;
  } catch (error) {
    console.error("Ошибка при получении данных:", error);
  }
}
