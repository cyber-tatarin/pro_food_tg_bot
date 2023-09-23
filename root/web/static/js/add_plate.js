let choicesCounter = 1;

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
        response.forEach((item) => {
          // console.log(item);
          if (item.meal_name === event.detail.choice.label) {
            console.log("measure", item.meal_name);
            setTimeout(() => {
              setTotalEnergy(response);
            }, 0);
          }
        });

        el.parentElement.style.color = "#303030";
      },
      false
    );
    choices.setChoices(data, "value", "label", false);
  });
};

let testChoices = [];
let response;

const buttonAdd = document.querySelector(".dish__add");
buttonAdd.addEventListener("click", async (event) => {
  event.preventDefault();
  document.querySelector(".dish__remove").classList.add("dish__remove_active");
  document.querySelector(".dish__remove").disabled = false;
  buttonAdd.parentElement.insertAdjacentHTML(
    "beforebegin",
    `<div class="dish__item dish__item_new">
    <p class="dish__title">Блюдо ${choicesCounter}</p>
    <select name="meal_id${choicesCounter}" class="js-choice_${choicesCounter} choice-energy">
      <option value="" selected>Введите ингридиент</option>
    
    </select>
    <div class="percentages">
              <p class="step__title">% в тарелке</p>
              <div class="percentages-flex">
                <div class="step__inner">
                  <input
                  checked
                    type="radio"    
                    name="meal_percentage${choicesCounter}"
                    class="step__margin"
                    id="percentage1_${choicesCounter}"
                  /><label for="percentage1_${choicesCounter}">25%</label>
                </div>
                <div class="step__inner">
                  <input
                    type="radio"
                    name="meal_percentage${choicesCounter}"
                    class="step__margin"
                    id="percentage2_${choicesCounter}"
                  /><label for="percentage2_${choicesCounter}">33%</label>
                </div>
                <div class="step__inner">
                  <input
                    type="radio"       
                    name="meal_percentage${choicesCounter}"            
                    class="step__margin"
                    id="percentage3_${choicesCounter}"
                  /><label for="percentage3_${choicesCounter}">50%</label>
                </div>
                <div class="step__inner">
                  <input
                    type="radio"    
                    name="meal_percentage${choicesCounter}"             
                    class="step__margin"
                    id="percentage4_${choicesCounter}"
                  /><label for="percentage4_${choicesCounter}">100%</label>
                </div>
              </div>
            </div>`
  );
  console.log(choicesCounter);
  renderSelect(response, testChoices);
});

const buttonRemove = document.querySelector(".dish__remove");
buttonRemove.addEventListener("click", (event) => {
  event.preventDefault();
  // console.log(buttonRemove.parentElement.previousSibling);
  buttonRemove.parentElement.previousSibling.remove();
  const items = document.querySelectorAll(".dish__item");
  if (items.length < 2) {
    document.querySelector(".dish__remove").disabled = true;
    document
      .querySelector(".dish__remove")
      .classList.remove("dish__remove_active");
  }
  choicesCounter--;
  setTotalEnergy(response);
});

const form = document.getElementById("form");

document
  .querySelector("form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const box = {};

    const checkboxes = document.querySelectorAll(".step__margin");
    let selectedCheckboxValue = null;
    for (const checkbox of checkboxes) {
      if (checkbox.checked) {
        const labelElement = document.querySelector(
          `label[for="${checkbox.id}"]`
        );

        const labelText = labelElement.textContent;
        const finalPercent = Number(labelText.slice(0, -1));

        selectedCheckboxValue = finalPercent;
        box[checkbox.name] = selectedCheckboxValue;
      }
    }

    const formData = new FormData(event.target);

    const data = {};
    formData.forEach((value, key) => {
      if (key !== "next_step") {
        data[key] = value;
      }
    });

    for (const key in box) {
      data[key] = box[key];
    }

    try {
      const request = await fetch("../api/add_plate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const response = await request.json();
      if (response.success === true) {
        console.log("fetched successfully!");
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
        console.log(response);
        document.querySelector(".error").classList.add("error_active");
      }
    } catch (err) {
      console.log(err);
    }
  });

async function getData() {
  try {
    const request = await fetch("../api/get_meals_list", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    response = await request.json();

    testChoices = response.map((item) => ({
      value: item.meal_id,
      label: item.meal_name,
    }));

    renderSelect(response, testChoices);

    return response;
  } catch (error) {
    console.error("Ошибка при получении данных:", error);
  }
}

getData();

function setTotalEnergy(data) {
  const dishAmount = document.querySelectorAll(`.choice-energy`);
  const totalEnergy = {};
  totalEnergy.calories = 0;
  totalEnergy.proteins = 0;
  totalEnergy.fats = 0;
  totalEnergy.carbohydrates = 0;

  dishAmount.forEach((item) => {
    const value = item.textContent;

    data.forEach((el) => {
      if (el.meal_name === value) {
        // console.log(el);
        totalEnergy.calories += +el.calories;
        totalEnergy.proteins += +el.proteins;
        totalEnergy.fats += +el.fats;
        totalEnergy.carbohydrates += +el.carbohydrates;
      }
    });
  });

  const totalCalories = document.querySelector(".dish__calories");

  totalCalories.textContent = `Общее КБЖУ приема пищи: ${totalEnergy.calories}  /  ${totalEnergy.proteins}  /  ${totalEnergy.fats}  /  ${totalEnergy.carbohydrates}`;
}

let tg = window.Telegram.WebApp;
let tg_id = tg.initDataUnsafe.user.id;

document.querySelector("#tg_id").value = tg_id;
