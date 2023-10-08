const tg = window.Telegram.WebApp;
const tg_id = 459471362 || tg.initDataUnsafe.user.id;

let plate_type;

const ref = String(document.referrer);

if (ref.includes("breakfast")) {
  plate_type = "Завтрак";
  document.querySelector(".meal-type").textContent =
    "Составить рацион на сегодня (Завтрак)";
} else if (ref.includes("lunch")) {
  plate_type = "Обед";
  document.querySelector(".meal-type").textContent =
    "Составить рацион на сегодня (Обед)";
} else if (ref.includes("dinner")) {
  document.querySelector(".meal-type").textContent =
    "Составить рацион на сегодня (Ужин)";
  plate_type = "Ужин";
}

async function sendData(link) {
  const request = await fetch(`..${link}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id, plate_type: plate_type }),
  });
  const response = await request.json();
  console.log(response);
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

function setPlateImage(className, plate, index) {
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

async function setPlates() {
  await getDiameter();

  const plates = await sendData("/api/get_all_favorites");

  plates.all_plates.forEach((plate, index) => {
    console.log(plate);
    document.querySelector(".cards").insertAdjacentHTML(
      "beforeend",
      `<div class="card card${index + 1}" name="${plate.plate_id}">
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
        data.plate_type = plate_type;
        sendPlate(data, "/api/has_chosen_plate", el.target);
      });

    setPlateImage("card__visual", plate, index);
    setPlateStars("card__stars", plate, index);
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
    </div>
  </div>`
    );

    setMealsList(plates.chosen_plate.meals, "card__list-chosen", index);
    setPlateImage("card__visual-chosen", plates.chosen_plate, 1);
    setPlateStars("card__stars-chosen", plates.chosen_plate, index);
  }

  if (plates.chosen_plate === null && plates.all_plates.length === 0) {
    document.querySelector(".empty-list").classList.remove("empty-list_hidden");
  }
}

setPlates();

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
      if (plate_type === "Завтрак") {
        window.location.href = "../choose_lunch";
      } else if (plate_type === "Обед") {
        window.location.href = "../choose_dinner";
      } else {
        window.location.href = "../main";
      }
    }
  } catch (e) {}
}