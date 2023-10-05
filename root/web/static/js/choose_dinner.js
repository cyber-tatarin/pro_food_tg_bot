const tg = window.Telegram.WebApp;
const tg_id = tg.initDataUnsafe.user.id;

const elements = document.querySelectorAll(`.js-choice_type`);
elements.forEach((el) => {
  const choices = new Choices(el, {
    itemSelectText: "",
    noResultsText: "Не найдено",
    searchEnabled: false,
    searchChoices: false,
  });
});

function setMealsList(meals, containerSelector, index) {
  meals.forEach((el, i) => {
    document
      .querySelector(`.${containerSelector}${index + 1}`)
      .insertAdjacentHTML(
        "beforeend",
        `<p class="card__list__item">${i + 1}. ${el}</p>`
      );
  });
}

async function sendData(link) {
  const request = await fetch(`..${link}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id, plate_type: "Ужин" }),
  });
  const response = await request.json();
  console.log(response);
  return response;
}

function setPlateImgae(className, plate, index) {
  let imagePath = "";
  if (plate.percentages[0] === "100") {
    imagePath = "../static/images/1-part.svg";
  } else if (plate.percentages[0] === "50") {
    imagePath = "../static/images/2-parts.svg";
  } else if (plate.percentages[0] === "33") {
    imagePath = "../static/images/3-33-parts.svg";
  } else if (plate.percentages[0] === "25" && plate.percentages[2] === "50") {
    imagePath = "../static/images/3-parts.svg";
  } else {
    imagePath = "../static/images/4-parts.svg";
  }
  document
    .querySelector(`.${className}${index + 1}`)
    .insertAdjacentHTML(
      "afterbegin",
      `<img src="${imagePath}" class="card__plate" />`
    );
}

function setPlateStars(className, plate, index) {
  const cardStarsElement = document.querySelector(`.${className}${index + 1}`);
  const greenStarImage = '<img src="../static/images/green-star.svg" alt="" />';
  const grayStarImage = '<img src="../static/images/gray-star.svg" alt="" />';

  for (let i = 1; i < 6; i++) {
    const starImage =
      i <= plate.recipe_difficulty ? greenStarImage : grayStarImage;
    cardStarsElement.insertAdjacentHTML("beforeend", starImage);
  }
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

    setMealsList(plate.meals, "card__list", index);

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
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        data.plate_type = "Ужин";
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

    setPlateImgae("card__visual", plate, index);
    setPlateStars("card__stars", plate, index);
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

    setMealsList(plate.meals, "card__list-mini", index);

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
        data.plate_type = "Ужин";
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
      .querySelector(`.card__button__favourites-mini${index + 1}`)
      .addEventListener("click", (el) => {
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        sendFavoritePlate(data, "/api/add_to_favorites", el.target);
      });

    setPlateStars("card__stars-mini", plate, index);
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

    setMealsList(plates.chosen_plate.meals, "card__list-chosen", index);

    setPlateImgae("card__visual-chosen", plates.chosen_plate, index);
    setPlateStars("card__stars-chosen", plates.chosen_plate, index);
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
      window.location.href = "../main";
    }
  } catch (e) {}
}
