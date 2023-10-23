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
  el.addEventListener(
    "change",
    function (event) {
      const choice = event.detail.value;
      sortCards(choice);
    },
    false
  );
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
  return response;
}

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

let diameter;
let promises = [];

async function getDiameter() {
  const request = await fetch(`../api/get_user_parameters`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id }),
  });
  const response = await request.json();
  diameter = response.plate_diameter;
  return response.plate_diameter;
}

async function setPlateImage(className, plate, index) {
  let imagePath = "";
  if (plate.percentages[0] === "100") {
    imagePath = "../static/images/1-part.png";
  } else if (plate.percentages[0] === "50" && plate.percentages.length === 2) {
    imagePath = "../static/images/2-parts.png";
  } else if (plate.percentages[0] === "33") {
    imagePath = "../static/images/3-33-parts.png";
  } else if (plate.percentages.length === 4) {
    imagePath = "../static/images/4-parts.png";
  } else {
    imagePath = "../static/images/3-parts.png";
  }

  let img = new Image();
  let imgLoaded = new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
  });
  img.src = imagePath;
  img.className = "card__plate";
  document.querySelector(`.${className}${index + 1}`).appendChild(img);
  document
    .querySelector(`.${className}${index + 1}`)
    .insertAdjacentElement("afterbegin", img);

  return imgLoaded;
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
      <button class="card__button__recepi card__button__recepi-recommended${
        index + 1
      }">Рецепт</button>
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
      .querySelector(`.card__button__recepi-recommended${index + 1}`)
      .addEventListener("click", (event) => {
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        setRecepi(data);
        showRecepi();
      });

    document
      .querySelector(`.card__button__choose${index + 1}`)
      .addEventListener("click", (el) => {
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

    promises.push(setPlateImage("card__visual", plate, index));
    setPlateStars("card__stars", plate, index);
  });

  plates.all_plates.forEach((plate, index) => {
    document.querySelector(".cards-mini").insertAdjacentHTML(
      "beforeend",
      `<div class="card card-mini card-mini${index + 1}" name="${
        plate.plate_id
      }">
    <div class="card__calories">Б: ${plate.proteins} / Ж: ${plate.fats} / У: ${
        plate.carbohydrates
      } / ${plate.calories} ккал</div>
    <div class="card__meal card__meal-mini">“${plate.plate_name}”</div>
    <p class="card__list-description">Список блюд</p>
    <div class="card__list card__list-mini${index + 1}">
    </div>
    <p class="card__difficulty card__difficulty-mini${index + 1}">Сложность</p>
    <div class="card__stars card__stars-mini card__stars-mini${index + 1}">
    </div>
    <p class="total-time">Общее время приготовления</p>
    <p class="total-time_value">${plate.recipe_time} минут</p>
    <p class="active-time">Активное время приготовления</p>
    <p class="active-time_value">${plate.recipe_active_time} минут</p>
    <div class="card__buttons">
      <button class="card__button__recepi card__button__recepi${
        index + 1
      }">Рецепт</button>
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
      .querySelector(`.card__button__recepi${index + 1}`)
      .addEventListener("click", (event) => {
        const data = {};
        data.plate_id = plate.plate_id;
        data.tg_id = tg_id;
        setRecepi(data);
        showRecepi();
      });

    document
      .querySelector(`.card__button__choose-mini${index + 1}`)
      .addEventListener("click", (el) => {
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
    <div class="card__visual card__visual-chosen card__visual-chosen1">
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
    <div class="card__list card__list-chosen card__list-chosen1">
    </div>
    <p class="card__difficulty card__difficulty-chosen">Сложность</p>
    <div class="card__stars card__stars-chosen card__stars-chosen1">
    </div>
    <p class="total-time">Общее время приготовления</p>
    <p class="total-time_value">${plates.chosen_plate.recipe_time} минут</p>
    <p class="active-time">Активное время приготовления</p>
    <p class="active-time_value">${plates.chosen_plate.recipe_active_time} минут</p>
    <div class="card__buttons">
      <button class="card__button__recepi card__button__recepi-favourite">Рецепт</button>
      <button class="card__button__favourites card__button__favourites-chosen">Добавить в избранное</button>
    </div>
  </div>`
    );

    setMealsList(plates.chosen_plate.meals, "card__list-chosen", 0);

    if (plates.chosen_plate.in_favorites === true) {
      document.querySelector(`.card__button__favourites-chosen`).textContent =
        "Удалить из избранного";
      document
        .querySelector(`.card__button__favourites-chosen`)
        .classList.add("card__button__favourites_off");
    }

    promises.push(setPlateImage("card__visual-chosen", plates.chosen_plate, 0));
    setPlateStars("card__stars-chosen", plates.chosen_plate, 0);

    document
      .querySelector(`.card__button__recepi-favourite`)
      .addEventListener("click", (event) => {
        const data = {};
        data.plate_id = plates.chosen_plate.plate_id;
        data.tg_id = tg_id;
        setRecepi(data);
        showRecepi();
      });

    document
      .querySelector(`.card__button__favourites-chosen`)
      .addEventListener("click", (el) => {
        const data = {};
        data.plate_id = plates.chosen_plate.plate_id;
        data.tg_id = tg_id;
        sendFavoritePlate(data, "/api/add_to_favorites", el.target);
      });
  }
}

let isFunctionsLoaded = false;
let isImagesLoaded = false;

setPlates().finally(() => {
  Promise.all(promises)
    .then(() => {
      isFunctionsLoaded = true;
      if (isImagesLoaded) {
        hideLoading();
      }
    })
    .catch(() => {
      console.log("Ошибка при загрузке одного или нескольких изображений.");
      isFunctionsLoaded = true;
      if (isImagesLoaded) {
        hideLoading();
      }
    });
});

function showLoading(param = true) {
  const loader = document.querySelector(".loading");
  loader.classList.remove("loading_hidden");
  loader.style.display = "flex";
  if (param) {
    document.body.style.overflow = "hidden";
  }
}

function hideLoading(param = true) {
  const loader = document.querySelector(".loading");
  loader.classList.add("loading_hidden");
  loader.addEventListener("transitionend", function () {
    loader.style.display = "none";
  });
  if (param) {
    document.body.style.overflow = "visible";
  }
}

window.onload = () => {
  isImagesLoaded = true;
  if (isFunctionsLoaded) {
    hideLoading();
  }
};

async function sendFavoritePlate(data, link, el) {
  try {
    showLoading();
    const request = await fetch(`..${link}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const response = await request.json();
    hideLoading();
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
    showLoading();
    const request = await fetch(`..${link}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const response = await request.json();

    if (response.success === true) {
      window.location.href = "../choose_lunch";
    } else {
      hideLoading();
    }
  } catch (e) {}
}

function showRecepi() {
  document.querySelector(".popup").classList.remove("popup_hidden");
  document.body.style.overflow = "hidden";
}

async function setRecepi(data) {
  showLoading(false);
  document.querySelector(".popup__inner").innerHTML = "";
  document.querySelector(".popup__inner").insertAdjacentHTML(
    "afterbegin",
    ` <p class="popup__plate-title">
  “”
</p>
<div class="exit">
  <img src="../static/images/exit.svg" alt="exit" />
</div>`
  );

  const exit = document.querySelector(".exit");
  exit.addEventListener("click", (event) => {
    event.target.closest(".popup").classList.add("popup_hidden");
    document.body.style.overflow = "visible";
  });

  const request = await fetch(`../api/get_recipe`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  const response = await request.json();

  hideLoading(false);

  document.querySelector(
    ".popup__plate-title"
  ).textContent = `“${response.plate_name}”`;

  response.meals.forEach((meal, index) => {
    document.querySelector(".popup__inner").insertAdjacentHTML(
      "beforeend",
      `<div class="popup__meal popup__meal${index + 1}">
    <p class="popup__meal-title popup__meal-title${index + 1}">${index + 1}. ${
        meal.meal_name
      }</p>
    <p class="popup__ingredients">Ингредиенты:</p>
    <div class="popup__ingredients-flex popup__ingredients-flex${index + 1}">
    </div>
    <p class="popup__recepi">Рецепт:</p>
    <p class="popup__recepi__text">
      ${meal.recipe}
    </p>
    <div class="popup__time">
      <div class="popup__time-flex">
        <p class="popup__time-current">Активное время (минут)</p>
        <p class="popup__time-current__value">${meal.recipe_active_time}</p>
      </div>
      <div class="popup__time-flex">
        <p class="popup__time-total">Общее время (минут)</p>
        <p class="popup__time-total__value">${meal.recipe_time}</p>
      </div>
    </div>
    <hr class="hr hr-20" />
  </div>`
    );

    meal.ingredients.forEach((ingredient, i) => {
      document
        .querySelector(`.popup__ingredients-flex${index + 1}`)
        .insertAdjacentHTML(
          "beforeend",
          ` <div class="popup__ingredients${i + 1}">
        <p class="popup__ingredients__title"><span class="number-indicator">${
          i + 1
        }.</span> ${ingredient.ingredient_name}</p>
        <p class="popup__ingredients__amount">количество: ${
          ingredient.ingredient_amount
        }</p>
        <p class="popup__ingredients__measure">мера: ${
          ingredient.ingredient_measure
        }</p>
      </div>`
        );
    });
  });
}

function sortCards(option) {
  const container = document.querySelector(".cards-mini");
  const blocks = Array.from(container.children);
  const sortingFunctions = {
    1: (a, b) => compareByStarCount(a, b),
    2: (a, b) => compareByStarCount(b, a),
    3: (a, b) => compareByRecipeTime(a, b),
    4: (a, b) => compareByRecipeTime(b, a),
  };

  const sortingFunction = sortingFunctions[option] || sortingFunctions["1"];
  blocks.sort(sortingFunction);

  container.innerHTML = "";
  blocks.forEach((block) => {
    container.appendChild(block);
  });
}

function compareByStarCount(cardA, cardB) {
  const starsA = cardA.querySelectorAll(
    '.card__stars-mini img[src="../static/images/green-star.svg"]'
  ).length;
  const starsB = cardB.querySelectorAll(
    '.card__stars-mini img[src="../static/images/green-star.svg"]'
  ).length;
  return starsA - starsB;
}

function compareByRecipeTime(cardA, cardB) {
  const timeA =
    parseFloat(cardA.querySelector(".active-time_value").textContent) || 0;
  const timeB =
    parseFloat(cardB.querySelector(".active-time_value").textContent) || 0;
  return timeA - timeB;
}
