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
        console.log("label", event.detail.choice.label);
        console.log("value", event.detail.choice.value);
        // console.log(response.length);
        // response.forEach((item) => {
        //   console.log(item["ingredient_id"]);
        //   console.log(event.detail.choice.value);
        //   if (
        //     item["ingredient_id"] ===
        //     response[event.detail.choice.value]["ingredient_id"]
        //   ) {
        //     console.log(1);
        //   }
        // });

        // const dish__amount = document.querySelector(
        //   `.dish__amount${choicesCounter--}`
        // );
        // console.log(test, choicesCounter);
        // dish__amount.innerHTML =
        //   test[choicesCounter].calories +
        //   "  /  " +
        //   test[choicesCounter].proteins +
        //   "  /  " +
        //   test[choicesCounter].fats +
        //   "  /  " +
        //   test[choicesCounter].carbohydrates;
        el.parentElement.style.color = "#303030";
      },
      false
    );
    console.log("data", data);
    choices.setChoices(data, "value", "label", false);
  });
};

let testChoices = [];
let response;

// renderSelect();

const button = document.querySelector(".dish__add");
button.addEventListener("click", async (event) => {
  event.preventDefault();
  button.insertAdjacentHTML(
    "beforebegin",
    `<div class="dish__item dish__item_new">
    <p class="dish__title">Блюдо ${choicesCounter}</p>
    <select name="meal_id${choicesCounter}" class="js-choice_${choicesCounter}">
      <option value="" selected>Введите ингридиент</option>
    
    </select>
    <div class="percentages">
              <p class="step__title">% в тарелке</p>
              <div class="percentages-flex">
                <div class="step__inner">
                  <input
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

  // const elements = document.querySelectorAll(`.js-choice_${choicesCounter++}`);
  // elements.forEach((el) => {
  //   const choices = new Choices(el, {
  //     itemSelectText: "",
  //     noResultsText: "Не найдено",
  //   });
  //   el.addEventListener(
  //     "choice",
  //     function (event) {
  //       el.parentElement.style.color = "#303030";
  //     },
  //     false
  //   );
  // });
});

const form = document.getElementById("form");

document
  .querySelector("form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const box = {};

    const checkboxes = document.querySelectorAll(".step__margin");
    // console.log(checkboxes);

    // Найдите выбранный чекбокс
    let selectedCheckboxValue = null;
    for (const checkbox of checkboxes) {
      if (checkbox.checked) {
        // console.log("check", checkbox);

        // Найдите соответствующий <label>
        const labelElement = document.querySelector(
          `label[for="${checkbox.id}"]`
        );

        // Получите текст из <label>
        const labelText = labelElement.textContent;
        const finalPercent = Number(labelText.slice(0, -1));

        selectedCheckboxValue = finalPercent;
        box[checkbox.name] = selectedCheckboxValue;
        // break; // Если выбран чекбокс, можно прервать цикл
      }
    }

    // console.log(selectedCheckboxValue);
    // console.log("box", box);

    // Collect form data
    const formData = new FormData(event.target);

    // Convert form data to JSON
    const data = {};
    formData.forEach((value, key) => {
      if (key !== "next_step") {
        data[key] = value;
      }
    });

    for (const key in box) {
      data[key] = box[key];
    }

    // console.log("fetched", data);
    // Send JSON data to the backend
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
    // console.log("response", response);

    testChoices = response.map((item) => ({
      value: item.meal_id,
      label: item.meal_name,
    }));
    // console.log(testChoices);
    renderSelect(response, testChoices);
    // const dish__amount = document.querySelector(
    //   `.dish__amount${choicesCounter - 1}`
    // );

    // dish__amount.innerHTML =
    //   response[choicesCounter - 1].calories +
    //   "  /  " +
    //   response[choicesCounter - 1].proteins +
    //   "  /  " +
    //   response[choicesCounter - 1].fats +
    //   "  /  " +
    //   response[choicesCounter - 1].carbohydrates;
    return response;
  } catch (error) {
    console.error("Ошибка при получении данных:", error);
  }
}

getData();

let tg = window.Telegram.WebApp;
let tg_id = tg.initDataUnsafe.user.id;

document.querySelector("#tg_id").value = tg_id;
