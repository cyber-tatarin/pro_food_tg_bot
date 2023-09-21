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
        document
          .querySelectorAll(".choices__inner")
          .forEach((el) => (el.style.color = "#303030"));
      },
      false
    );
  });
};

renderSelect();

const form = document.getElementById("form");

document
  .querySelector("form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const checkboxes = document.querySelectorAll(".step_radio");

    // Найдите выбранный чекбокс
    let selectedCheckboxValue = null;
    for (const checkbox of checkboxes) {
      if (checkbox.checked) {
        selectedCheckboxValue = checkbox.id;
        break; // Если выбран чекбокс, можно прервать цикл
      }
    }

    console.log(selectedCheckboxValue);

    // Collect form data
    const formData = new FormData(event.target);

    // Convert form data to JSON
    const data = {};
    let selectedCheckbox;
    formData.forEach((value, key) => {
      if (key !== "next_step") {
        data[key] = value;
      } else {
        selectedCheckbox = value;
      }
    });
    console.log("fetched!!!!!!!!!!!!!!!!!");
    // data.delete("next_step");
    // data["next_step"] = selectedCheckboxValue;
    console.log(data);
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
      console.log(response);
      if (response.success === true) {
        console.log("redirect");
        window.location.href = "../add_meal";
      } else {
        console.log(response.status);
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
    const response = await request.json();

    console.log(response);
    return response;
  } catch (error) {
    console.error("Ошибка при получении данных:", error);
  }
}

// Добавление обработчика события DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
  getData(); // Вызывает функцию после полной загрузки HTML
});
