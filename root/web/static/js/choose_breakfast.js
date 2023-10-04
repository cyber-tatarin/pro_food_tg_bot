let tg = window.Telegram.WebApp;
let tg_id = tg.initDataUnsafe.user.id;

const elements = document.querySelectorAll(`.js-choice_type`);
elements.forEach((el) => {
  const choices = new Choices(el, {
    itemSelectText: "",
    noResultsText: "Не найдено",
    searchEnabled: false,
    searchChoices: false,
  });
});

async function sendData(link) {
  const request = await fetch(`..${link}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id, plate_type: "Завтрак" }),
  });
  const response = await request.json();
  console.log(response);
  return response;
}

let diameter;

async function getDiameter() {
  const request = await fetch(`../api/get_user_parameters`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id }),
  });
  const response = await request.json();
  console.log(response);
  diameter = response.plate_diameter;
  return response.plate_diameter;
}

async function setPlates() {
  await getDiameter();

  const plates = await sendData("/api/get_all_plates_to_choose");

  plates.recommended_plates.forEach((plate, index) => {
    console.log(plate);
    document.querySelector(".cards").insertAdjacentHTML(
      "beforeend",
      `<div class="card card${index + 1}" name="${plate.plate_id}">
    <div class="card__type">Рекомендуем</div>
    <div class="card__calories">Б: ${plate.proteins} / Ж: ${plate.fats} / У: ${
        plate.carbohydrates
      } / ${plate.calories} ккал</div>
    <div class="card__meal">“${plate.plate_name}”</div>
    <div class="card__visual card__visual${index + 1}">
      <div class="card__plate_frames"></div>
      <div class="card__plate_size">
        <div class="plate__arrow">
          <img src="../static/images/plate-arrow.svg" alt="" />
        </div>
        <div class="plate__size-title plate-diameter-value">
          ${diameter} см
        </div>
      </div>
    </div>
    <p class="card__list-description">Список блюд</p>
    <div class="card__list card__list${index + 1}">
    </div>
    <p class="card__difficulty card__difficulty${index + 1}">Сложность</p>
    <div class="card__stars card__stars${index + 1}">
    </div>
    <p class="total-time">Общее время приготовления</p>
    <p class="total-time_value">${plate.recipe_time} минут</p>
    <p class="active-time">Активное время приготовления</p>
    <p class="active-time_value">${plate.recipe_active_time} минут</p>
    <div class="card__buttons">
      <button class="card__button__recepi">Рецепт</button>
      <button class="card__button__favourites card__button__favourites${
        index + 1
      }">Добавить в избранное</button>
      <button class="card__button__choose card__button__choose${
        index + 1
      }">Выбрать</button>
    </div>
  </div>`
    );

    plate.meals.forEach((el, i) => {
      document
        .querySelector(`.card__list${index + 1}`)
        .insertAdjacentHTML(
          "beforeend",
          `<p class="card__list__item">${i + 1}. ${el}</p>`
        );
    });

    if (plate.is_eaten === true) {
      document.querySelector(`.card__button__choose${index + 1}`).textContent =
        "Не съел";
      document
        .querySelector(`.card__button__choose${index + 1}`)
        .classList.add("card__button__choose_off");
    }

    document
      .querySelector(`.card__button__choose${index + 1}`)
      .addEventListener("click", (el) => {
        // console.log("button", el.target);
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        data.plate_type = "Завтрак";
        sendPlate(data, "/api/has_chosen_plate", el.target);
      });

    if (plate.in_favorites === true) {
      document.querySelector(
        `.card__button__favourites${index + 1}`
      ).textContent = "Удалить из избранного";
      document
        .querySelector(`.card__button__favourites${index + 1}`)
        .classList.add("card__button__favourites_off");
    }

    document
      .querySelector(`.card__button__favourites${index + 1}`)
      .addEventListener("click", (el) => {
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        sendFavoritePlate(data, "/api/add_to_favorites", el.target);
      });

    if (plate.percentages[0] === "100") {
      console.log(1);
      document
        .querySelector(`.card__visual${index + 1}`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/1-part.svg" class="card__plate" />`
        );
    } else if (plate.percentages[0] === "50") {
      console.log(2);

      document
        .querySelector(`.card__visual${index + 1}`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/2-parts.svg" class="card__plate" />`
        );
    } else if (plate.percentages[0] === "33") {
      console.log(3);

      document
        .querySelector(`.card__visual${index + 1}`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/3-33-parts.svg" class="card__plate" />`
        );
    } else if (plate.percentages[0] === "25" && plate.percentages[2] === "50") {
      console.log(4);

      document
        .querySelector(`.card__visual${index + 1}`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/3-parts.svg" class="card__plate" />`
        );
    } else if (plate.percentages[0] === "25" && plate.percentages[1] === "25") {
      console.log(5);
      document
        .querySelector(`.card__visual${index + 1}`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/4-parts.svg" class="card__plate" />`
        );
    }

    for (let i = 1; i < 6; i++) {
      if (i <= plate.recipe_difficulty) {
        console.log("green-star");
        document
          .querySelector(`.card__stars${index + 1}`)
          .insertAdjacentHTML(
            "beforeend",
            `<img src="../static/images/green-star.svg" alt="" />`
          );
      } else {
        console.log("grey-star");
        document
          .querySelector(`.card__stars${index + 1}`)
          .insertAdjacentHTML(
            "beforeend",
            `<img src="../static/images/gray-star.svg" alt="" />`
          );
      }
    }
  });

  plates.all_plates.forEach((plate, index) => {
    document.querySelector(".cards-mini").insertAdjacentHTML(
      "beforeend",
      `<div class="card card-mini card-mini${index + 1}" name="${
        plate.plate_id
      }">
    <div class="card__type">Рекомендуем</div>
    <div class="card__calories">Б: ${plate.proteins} / Ж: ${plate.fats} / У: ${
        plate.carbohydrates
      } / ${plate.calories} ккал</div>
    <div class="card__meal card__meal-mini">“${plate.plate_name}”</div>
    <p class="card__list-description">Список блюд</p>
    <div class="card__list card__list-mini${index + 1}">
    </div>
    <p class="card__difficulty card__difficulty-mini${index + 1}">Сложность</p>
    <div class="card__stars card__stars-mini${index + 1}">
    </div>
    <p class="total-time">Общее время приготовления</p>
    <p class="total-time_value">${plate.recipe_time} минут</p>
    <p class="active-time">Активное время приготовления</p>
    <p class="active-time_value">${plate.recipe_active_time} минут</p>
    <div class="card__buttons">
      <button class="card__button__recepi">Рецепт</button>
      <button class="card__button__favourites card__button__favourites-mini${
        index + 1
      }">Добавить в избранное</button>
      <button class="card__button__choose card__button__choose-mini${
        index + 1
      }">Выбрать</button>
    </div>
  </div>`
    );

    plate.meals.forEach((el, i) => {
      document
        .querySelector(`.card__list-mini${index + 1}`)
        .insertAdjacentHTML(
          "beforeend",
          `<p class="card__list__item">${i + 1}. ${el}</p>`
        );
    });

    if (plate.is_eaten === true) {
      document.querySelector(
        `.card__button__choose-mini${index + 1}`
      ).textContent = "Не съел";
      document
        .querySelector(`.card__button__choose-mini${index + 1}`)
        .classList.add("card__button__choose_off");
    }

    document
      .querySelector(`.card__button__choose-mini${index + 1}`)
      .addEventListener("click", (el) => {
        // console.log("button", el.target);
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        data.plate_type = "Завтрак";
        sendPlate(data, "/api/has_chosen_plate", el.target);
      });

    if (plate.in_favorites === true) {
      document.querySelector(
        `.card__button__favourites-mini${index + 1}`
      ).textContent = "Удалить из избранного";
      document
        .querySelector(`.card__button__favourites-mini${index + 1}`)
        .classList.add("card__button__favourites_off");
    }

    document
      .querySelector(`.card__button__favourites${index + 1}`)
      .addEventListener("click", (el) => {
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        sendFavoritePlate(data, "/api/add_to_favorites", el.target);
      });

    for (let i = 1; i < 6; i++) {
      if (i <= plate.recipe_difficulty) {
        console.log("green-star");
        document
          .querySelector(`.card__stars-mini${index + 1}`)
          .insertAdjacentHTML(
            "beforeend",
            `<img src="../static/images/green-star.svg" alt="" />`
          );
      } else {
        console.log("grey-star");
        document
          .querySelector(`.card__stars-mini${index + 1}`)
          .insertAdjacentHTML(
            "beforeend",
            `<img src="../static/images/gray-star.svg" alt="" />`
          );
      }
    }
  });

  if (plates.chosen_plate !== null) {
    document.querySelector(".cards").insertAdjacentHTML(
      "afterbegin",
      `<div class="card" name="${plates.chosen_plate.plate_id}">
    <div class="card__type">Выбрано</div>
    <div class="card__calories">Б: ${plates.chosen_plate.proteins} / Ж: ${plates.chosen_plate.fats} / У: ${plates.chosen_plate.carbohydrates} / ${plates.chosen_plate.calories} ккал</div>
    <div class="card__meal">“${plates.chosen_plate.plate_name}”</div>
    <div class="card__visual card__visual-chosen">
      <div class="card__plate_frames"></div>
      <div class="card__plate_size">
        <div class="plate__arrow">
          <img src="../static/images/plate-arrow.svg" alt="" />
        </div>
        <div class="plate__size-title plate-diameter-value">
          ${diameter} см
        </div>
      </div>
    </div>
    <p class="card__list-description">Список блюд</p>
    <div class="card__list card__list-chosen">
    </div>
    <p class="card__difficulty card__difficulty-chosen">Сложность</p>
    <div class="card__stars card__stars-chosen">
    </div>
    <p class="total-time">Общее время приготовления</p>
    <p class="total-time_value">${plates.chosen_plate.recipe_time} минут</p>
    <p class="active-time">Активное время приготовления</p>
    <p class="active-time_value">${plates.chosen_plate.recipe_active_time} минут</p>
    <div class="card__buttons">
      <button class="card__button__recepi">Рецепт</button>
      <button class="card__button__favourites card__button__favourites-chosen">Добавить в избранное</button>
    </div>
  </div>`
    );

    plates.chosen_plate.meals.forEach((el, i) => {
      document
        .querySelector(`.card__list-chosen`)
        .insertAdjacentHTML(
          "beforeend",
          `<p class="card__list__item">${i + 1}. ${el}</p>`
        );
    });

    if (plates.chosen_plate.in_favorites === true) {
      document.querySelector(`.card__button__favourites-chosen`).textContent =
        "Удалить из избранного";
      document
        .querySelector(`.card__button__favourites-chosen`)
        .classList.add("card__button__favourites_off");
    }

    if (plates.chosen_plate.percentages[0] === "100") {
      document
        .querySelector(`.card__visual-chosen`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/1-part.svg" class="card__plate" />`
        );
    } else if (plates.chosen_plate.percentages[0] === "50") {
      document
        .querySelector(`.card__visual-chosen`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/2-parts.svg" class="card__plate" />`
        );
    } else if (plates.chosen_plate.percentages[0] === "33") {
      document
        .querySelector(`.card__visual-chosen`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/3-33-parts.svg" class="card__plate" />`
        );
    } else if (
      plates.chosen_plate.percentages[0] === "25" &&
      plates.chosen_plate.percentages[2] === "50"
    ) {
      document
        .querySelector(`.card__visual-chosen`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/3-parts.svg" class="card__plate" />`
        );
    } else {
      document
        .querySelector(`.card__visual-chosen`)
        .insertAdjacentHTML(
          "afterbegin",
          `<img src="../static/images/4-parts.svg" class="card__plate" />`
        );
    }

    for (let i = 1; i < 6; i++) {
      if (i <= plates.chosen_plate.recipe_difficulty) {
        document
          .querySelector(`.card__stars-chosen`)
          .insertAdjacentHTML(
            "beforeend",
            `<img src="../static/images/green-star.svg" alt="" />`
          );
      } else {
        document
          .querySelector(`.card__stars-chosen`)
          .insertAdjacentHTML(
            "beforeend",
            `<img src="../static/images/gray-star.svg" alt="" />`
          );
      }
    }
  }
}

setPlates();

async function sendFavoritePlate(data, link, el) {
  try {
    const request = await fetch(`..${link}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const response = await request.json();
    // console.log(response);
    if (response.success === true) {
      if (response.is_black === true) {
        el.textContent = "Добавить в избранное";
        el.classList.remove("card__button__favourites_off");
      } else {
        el.textContent = "Удалить из избранного";
        el.classList.add("card__button__favourites_off");
      }
    }
  } catch (err) {
    console.log(err);
  }
}

async function sendPlate(data, link, el) {
  try {
    const request = await fetch(`..${link}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const response = await request.json();
    console.log(response);
    if (response.success === true) {
      window.location.href = "../choose_lunch";
    }
  } catch (e) {}
}
