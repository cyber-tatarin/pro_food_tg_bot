let choicesCounter = 1;

const test = getData(); //

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
    console.log(data);
    choices.setChoices(data, "value", "label", false);
  });
};

// const test = [
//   {
//     meal_id: 1,
//     meal_name: "A",
//     calories: 1,
//     proteins: 20,
//     fats: 300,
//     carbohydrates: 400,
//   },
//   {
//     meal_id: 2,
//     meal_name: "B",
//     calories: 100,
//     proteins: 20,
//     fats: 3,
//     carbohydrates: 40,
//   },
//   {
//     meal_id: 3,
//     meal_name: "C",
//     calories: 10,
//     proteins: 20,
//     fats: 3000,
//     carbohydrates: 4,
//   },
// ];

let testChoices = [];
let response;

// renderSelect();

const button = document.querySelector(".dish__add");
button.addEventListener("click", (event) => {
  event.preventDefault();
  button.insertAdjacentHTML(
    "beforebegin",
    `<div class="dish__item dish__item_new">
    <p class="dish__title">Ингридиент ${choicesCounter} (в мере "ладонь")</p>
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
  // const dish__amount = document.querySelector(`.dish__amount${choicesCounter}`);
  // console.log(test, choicesCounter);
  // dish__amount.innerHTML =
  //   test[choicesCounter].calories +
  //   "  /  " +
  //   test[choicesCounter].proteins +
  //   "  /  " +
  //   test[choicesCounter].fats +
  //   "  /  " +
  //   test[choicesCounter].carbohydrates;

  // calculateAmountFromInputs();
});

const form = document.getElementById("form");

document
  .querySelector("form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    // Collect form data
    const formData = new FormData(event.target);

    // Convert form data to JSON
    const data = {};
    formData.forEach((value, key) => {
      if (key !== "next_step") {
        data[key] = value;
      }
    });
    console.log("data", data);
    console.log("fetched!!!!!!!!!!!!!!!!!");
    // Send JSON data to the backend
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
    console.log("response", response, choicesCounter);

    testChoices = response.map((item) => ({
      value: item.ingredient_id,
      label: item.ingredient_name,
    }));
    console.log(testChoices);
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

// Добавление обработчика события DOMContentLoaded
// document.addEventListener("DOMContentLoaded", function () {
//   console.log(choicesCounter - 1);
//   const dish__amount = document.querySelector(
//     `.dish__amount${choicesCounter - 1}`
//   );
//   console.log(test);
//   dish__amount.innerHTML =
//     test[choicesCounter].calories +
//     "  /  " +
//     test[choicesCounter].proteins +
//     "  /  " +
//     test[choicesCounter].fats +
//     "  /  " +
//     test[choicesCounter].carbohydrates;
// });

function calculateAmountFromInputs() {
  const inputs = document.querySelectorAll("input__amount");
  inputs.forEach((input) =>
    input.addEventListener("input", (event) => {
      const inputValue = event.target.value;
      const dishAmountElement = input.nextElementSibling;
      // Проверьте, является ли inputValue числом и не NaN
      if (inputValue === "") {
        dishAmountElement.textContent = `${test.calories}  /  ${test.proteins}  /  ${test.fats}  /  ${test.carbohydrates}`;
        // Теперь inputValue содержит введенное число
        console.log(inputValue);
      } else {
        dishAmountElement.textContent = `${test.calories * inputValue}  /  ${
          test.proteins * inputValue
        }  /  ${test.fats * inputValue}  /  ${test.carbohydrates * inputValue}`;
      }
      const totalCalories = document.querySelector(".dish__calories");
      totalCalories.textContent = `${test.calories * inputValue}  /  ${
        test.proteins * inputValue
      }  /  ${test.fats * inputValue}  /  ${test.carbohydrates * inputValue}`;
    })
  );
}

calculateAmountFromInputs();

let tg = window.Telegram.WebApp;
let tg_id = tg.initDataUnsafe.user.id;

document.querySelector("#tg_id").value = tg_id;
