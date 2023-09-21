let choicesCounter = 1;

const renderSelect = () => {
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
  });
};

renderSelect();

const button = document.querySelector(".dish__add");
button.addEventListener("click", async (event) => {
  event.preventDefault();
  button.insertAdjacentHTML(
    "beforebegin",
    `<div class="dish__item dish__item_new">
    <p class="dish__title">Блюдо ${choicesCounter}</p>
    <select name="meal_id${choicesCounter}" class="js-choice_${choicesCounter}">
      <option value="" selected>Введите ингридиент</option>
      <option value="1">Кафе</option>
      <option value="2">Финтес клуб</option>
      <option value="3">Пиццерия</option>
      <option value="4">Реклама</option>
      <option value="5">Салон красоты</option>
      <option value="6">Шаурмичная</option>
      <option value="7">Бургерная</option>
      <option value="8">Кальянная</option>
      <option value="9">Суши-бар</option>
      <option value="10">Интернет-магазин</option>
      <option value="11">Рыбалка</option>
      <option value="12">Пчеловодство</option>
      <option value="13">Медицина</option>
      <option value="14">Маркетинг</option>
    </select>
    <div class="percentages">
              <p class="step__title">% в тарелке</p>
              <div class="percentages-flex">
                <div class="step__inner">
                  <input
                    type="radio"
                    name="step${choicesCounter}"
                    class="step_radio"
                    id="close${choicesCounter}"
                  /><label for="close${choicesCounter}">25%</label>
                </div>
                <div class="step__inner">
                  <input
                    type="radio"
                    name="step${choicesCounter}"
                    class="step_radio"
                    id="add-ingredient${choicesCounter}"
                  /><label for="add-ingredient${choicesCounter}">33%</label>
                </div>
                <div class="step__inner">
                  <input
                    type="radio"
                    name="step${choicesCounter}"
                    class="step_radio"
                    id="add-dish${choicesCounter}"
                  /><label for="add-dish${choicesCounter}">50%</label>
                </div>
                <div class="step__inner">
                  <input
                    type="radio"
                    name="step${choicesCounter}"
                    class="step_radio"
                    id="add-meal${choicesCounter}"
                  /><label for="add-meal${choicesCounter}">100%</label>
                </div>
              </div>
            </div>`
  );
  console.log(choicesCounter);

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
  });
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
      data[key] = value;
    });
    console.log("fetched!!!!!!!!!!!!!!!!!");
    // Send JSON data to the backend
    try {
      const request = await fetch("../api/add_ingredient", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const response = await request.json();
      if (response.status === 200) {
        console.log("fetched successfully!");
      } else {
        console.log(response.status);
      }
    } catch (err) {
      console.log(err);
    }
  });
