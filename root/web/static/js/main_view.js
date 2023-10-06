const tg = window.Telegram.WebApp;
const tg_id = 459471362 || tg.initDataUnsafe.user.id;

async function sendData(link) {
  console.log(tg_id);
  const request = await fetch(`..${link}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: tg_id }),
  });
  const response = await request.json();
  console.log(response);
  return response;
}

let diameter = 0;
let nutrientStreak = {};

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

async function setUserParameters() {
  const userParameters = await sendData("/api/get_user_parameters");
  console.log(userParameters);
  diameter = userParameters.plate_diameter;
  document.querySelector(
    ".weight-value"
  ).textContent = `${userParameters.weight} кг`;
  document.querySelector(
    ".height-value"
  ).textContent = `${userParameters.height} см`;
  document.querySelector(".age-value").textContent = userParameters.age;

  document.querySelectorAll(".plate-diameter-value").forEach((el) => {
    el.textContent = `${userParameters.plate_diameter} см `;
  });
  document.querySelector(
    ".weight-aim-value"
  ).textContent = `${userParameters.weight_aim} кг`;
  if (userParameters.weight_gap >= 0) {
    document.querySelector(
      ".weight-gap-value"
    ).textContent = `(+${userParameters.weight_gap}) кг`;
  } else {
    document.querySelector(
      ".weight-gap-value"
    ).textContent = `(${userParameters.weight_gap}) кг`;
  }
}

async function setUserStreak() {
  const userStreak = await sendData("/api/get_current_streak");
  console.log(userStreak);
  document.querySelector(
    ".strick__time"
  ).textContent = `${userStreak.current_streak} дня подряд 🥳 `;
  document.querySelector(
    ".notion__p-motivation"
  ).textContent = `${userStreak.motivational_text}`;
  document.querySelector(
    ".notion__p-tomorrow"
  ).textContent = ` А завтра за все задания ты получишь ${userStreak.coins_per_completed_task_for_tomorrow} ЖИРкоинов!!`;
  document.querySelector(
    ".notion__p-completed"
  ).textContent = `Выполни сегодня все задания, чтобы получить ${userStreak.coins_per_completed_task} ЖИРкоинов`;
  document.querySelector(
    ".notion__p-inactivity"
  ).textContent = `Если ты не выполнишь ни одно задание, то потеряешь ${userStreak.coins_loss_for_inactivity}  ЖИРкоина`;
  userStreak.tasks.forEach((el) => {
    if (el.completed === true) {
      document.querySelector(".list").insertAdjacentHTML(
        "beforeend",
        `
      <li class="list__item">
        <span class="list__item__marker list__item__marker_active"></span>${el.text}
      </li>`
      );
    } else {
      document.querySelector(".list").insertAdjacentHTML(
        "beforeend",
        `
        <li class="list__item">
          <span class="list__item__marker"></span>${el.text}
        </li>`
      );
    }
  });
}

async function setNutrientParameters() {
  nutrientStreak = await sendData("/api/get_nutrient_parameters");
  console.log(nutrientStreak);
  const width = nutrientStreak.eaten_calories / nutrientStreak.day_calories;
  if (width > 1) {
    document.querySelector(".progress__foreground").style.width = "100%";
    document.querySelector(".progress__foreground").style.borderTopRightRadius =
      "3px";
    document.querySelector(
      ".progress__foreground"
    ).style.borderBottomRightRadius = "3px";
    document.querySelector(".progress__foreground").style.backgroundColor =
      "#ff0831";
  } else {
    document.querySelector(".progress__foreground").style.width = `${
      width * 80
    }%`;
  }
  document.querySelector(
    ".day_calories"
  ).textContent = `${nutrientStreak.day_calories} ккал`;
  document.querySelector(
    ".eaten-calories"
  ).textContent = `${nutrientStreak.eaten_calories}`;
  document.querySelector(
    ".progress__end"
  ).textContent = `${nutrientStreak.day_calories}`;
  document.querySelector(
    ".day__proteins"
  ).textContent = `${nutrientStreak.day_proteins}`;
  document.querySelector(
    ".eaten__proteins"
  ).textContent = `${nutrientStreak.eaten_proteins}`;
  document.querySelector(
    ".day__fats"
  ).textContent = `${nutrientStreak.day_fats}`;
  document.querySelector(
    ".eaten__fats"
  ).textContent = `${nutrientStreak.eaten_fats}`;
  document.querySelector(
    ".day__carbohydrates"
  ).textContent = `${nutrientStreak.day_carbohydrates}`;
  document.querySelector(
    ".eaten__carbohydrates"
  ).textContent = `${nutrientStreak.eaten_carbohydrates}`;
}

async function setPlates() {
  const plates = await sendData("/api/get_today_plates");
  if (plates.length === 0) {
    document
      .querySelector(".eat__buttons-single")
      .classList.remove("eat__buttons-single_hidden");
  } else {
    document
      .querySelector(".eat__buttons-single")
      .classList.remove("eat__buttons-single_hidden");
    document.querySelector(".eat__buttons-single").textContent =
      "Изменить рацион";
    plates.forEach((plate, index) => {
      document.querySelector(".cards").insertAdjacentHTML(
        "beforeend",
        `<div class="card card${index + 1}" name="${plate.plate_id}">
    <div class="card__type">${plate.plate_type}</div>
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
        document.querySelector(
          `.card__button__choose${index + 1}`
        ).textContent = "Не съел";
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
          data.calories = plate.calories;
          data.proteins = plate.proteins;
          data.fats = plate.fats;
          data.carbohydrates = plate.carbohydrates;
          data.plate_type = plate.plate_type;
          sendPlate(data, "/api/has_eaten_plate", el.target);
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

      setPlateImage("card__visual", plate, index);
      setPlateStars("card__stars", plate, index);
    });
  }
}

setUserParameters();
setUserStreak();
setNutrientParameters();
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
      const cards = document.querySelectorAll(".card");
      cards.forEach((card) => {
        if (data.plate_id === card.name) {
          const buttonText = response.is_black
            ? "Удалить из избранного"
            : "Добавить в избранное";
          card.querySelector(".card__button__favourites").textContent =
            buttonText;
          card
            .querySelector(".card__button__favourites")
            .classList.toggle(
              "card__button__favourites_off",
              !response.is_black
            );
        }
      });
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

    if (response.success === true) {
      const eatenCaloriesEl = document.querySelector(".eaten-calories");
      const eatenProteinsEl = document.querySelector(".eaten__proteins");
      const eatenFatsEl = document.querySelector(".eaten__fats");
      const eatenCarbohydratesEl = document.querySelector(
        ".eaten__carbohydrates"
      );
      const progressForeground = document.querySelector(
        ".progress__foreground"
      );

      el.textContent = response.is_green ? "Выбрать" : "Не съел";
      el.classList.toggle("card__button__choose_off", !response.is_green);

      eatenCaloriesEl.textContent =
        +eatenCaloriesEl.textContent +
        (response.is_green ? -data.calories : data.calories);
      eatenProteinsEl.textContent =
        +eatenProteinsEl.textContent +
        (response.is_green ? -data.proteins : data.proteins);
      eatenFatsEl.textContent =
        +eatenFatsEl.textContent + (response.is_green ? -data.fats : data.fats);
      eatenCarbohydratesEl.textContent =
        +eatenCarbohydratesEl.textContent +
        (response.is_green ? -data.carbohydrates : data.carbohydrates);

      const width = +eatenCaloriesEl.textContent / nutrientStreak.day_calories;
      const progressBarStyle = progressForeground.style;

      progressBarStyle.width = width > 1 ? "100%" : `${width * 80}%`;
      progressBarStyle.borderTopRightRadius =
        progressBarStyle.borderBottomRightRadius = width > 1 ? "3px" : "0px";
      progressBarStyle.backgroundColor = width > 1 ? "#ff0831" : "#05ff00";
    }
  } catch (err) {
    console.log(err);
  }
}
