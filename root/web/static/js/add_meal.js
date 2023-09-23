let choicesCounter = 1;

const test = getData();

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
        const input = el.closest(".dish__item").querySelector(".input__amount");

        response.forEach((item) => {
          if (item.ingredient_name === event.detail.choice.label) {
            console.log("measure", item.measure);
            el
              .closest(".dish__item")
              .querySelector(
                ".dish__title-measure"
              ).textContent = ` в мере ("${item.measure}")`;
            calculateAmountFromInputs(item, input);
          }
        });

        el.parentElement.style.color = "#303030";
      },
      false
    );
    console.log(data);
    choices.setChoices(data, "value", "label", false);
  });
};

let testChoices = [];
let response;

const buttonAdd = document.querySelector(".dish__add");
buttonAdd.addEventListener("click", (event) => {
  event.preventDefault();
  document.querySelector(".dish__remove").classList.add("dish__remove_active");
  document.querySelector(".dish__remove").disabled = false;
  buttonAdd.parentElement.insertAdjacentHTML(
    "beforebegin",
    `<div class="dish__item dish__item_new">
    <p class="dish__title">Ингридиент ${choicesCounter}<span class="dish__title-measure"></span></p>
    <select name="ingredient_id${choicesCounter}" class="js-choice_${choicesCounter}">
      <option value="" selected>Введите ингридиент</option>
    </select>
    <p class="dish__title">Количество</p>
    <input
      class="input input__amount input_grey"
      name="ingredient_amount${choicesCounter}"
      type="number"
      maxlength="100"
      placeholder="Введите количество на 1 порцию"
      required
    />
    <div class="dish__amount dish__amount${choicesCounter}">0  /  0  /  0 /  0</div>
    </div>`
  );
  renderSelect(response, testChoices);
});

const buttonRemove = document.querySelector(".dish__remove");
buttonRemove.addEventListener("click", (event) => {
  event.preventDefault();
  console.log(buttonRemove.parentElement.previousSibling);
  buttonRemove.parentElement.previousSibling.remove();
  const items = document.querySelectorAll(".dish__item");
  if (items.length < 2) {
    document.querySelector(".dish__remove").disabled = true;
    document
      .querySelector(".dish__remove")
      .classList.remove("dish__remove_active");
  }
  choicesCounter--;
  setTotalEnergy();
});

const form = document.getElementById("form");

document
  .querySelector("form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {};
    formData.forEach((value, key) => {
      if (key !== "next_step") {
        data[key] = value;
      }
    });
    console.log("data", data);
    console.log("fetched!!!!!!!!!!!!!!!!!");
    try {
      const request = await fetch("../api/add_meal", {
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
        console.log("fetched successfully!");
        document.querySelector(".error").classList.remove("error_active");
      } else {
        document.querySelector(".error").classList.add("error_active");
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

    testChoices = response.map((item) => ({
      value: item.ingredient_id,
      label: item.ingredient_name,
    }));
    renderSelect(response, testChoices);

    return response;
  } catch (error) {
    console.error("Ошибка при получении данных:", error);
  }
}

function calculateAmountFromInputs(data, input) {
  setLocalEnergy(input, data);
  setTotalEnergy();

  input.addEventListener("input", (event) => {
    setLocalEnergy(input, data);

    setTotalEnergy();
  });
}

function setLocalEnergy(input, data) {
  console.log(input, data);
  const inputValue = input.value;
  const dishAmountElement = input.nextElementSibling;

  if (inputValue === "") {
    dishAmountElement.textContent = `0  /  0  /  0  /  0`;
  } else {
    dishAmountElement.textContent = `${data.calories * inputValue}  /  ${
      data.proteins * inputValue
    }  /  ${data.fats * inputValue}  /  ${data.carbohydrates * inputValue}`;
  }
}

function setTotalEnergy() {
  const dishAmount = document.querySelectorAll(".dish__amount");
  const totalEnergy = {};
  totalEnergy.calories = 0;
  totalEnergy.proteins = 0;
  totalEnergy.fats = 0;
  totalEnergy.carbohydrates = 0;

  dishAmount.forEach((item) => {
    const amount = item.textContent.split("  /  ");
    totalEnergy.calories += +amount[0];
    totalEnergy.proteins += +amount[1];
    totalEnergy.fats += +amount[2];
    totalEnergy.carbohydrates += +amount[3];
  });
  console.log(totalEnergy);

  const totalCalories = document.querySelector(".dish__calories");

  totalCalories.textContent = `Общее КБЖУ блюда: ${totalEnergy.calories}  /  ${totalEnergy.proteins}  /  ${totalEnergy.fats}  /  ${totalEnergy.carbohydrates}`;
}

// calculateAmountFromInputs();

let tg = window.Telegram.WebApp;
let tg_id = tg.initDataUnsafe.user.id;

document.querySelector("#tg_id").value = tg_id;
