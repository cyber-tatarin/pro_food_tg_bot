async function sendData(link) {
  const request = await fetch(`..${link}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tg_id: 983672566 }),
  });
  const response = await request.json();
  console.log(response);
  return response;
}

async function setUserParameters() {
  const userParameters = await sendData("/api/get_user_parameters");
  console.log(userParameters);
  document.querySelector(
    ".weight-value"
  ).textContent = `${userParameters.weight} кг `;
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
  document.querySelector(
    ".weight-gap-value"
  ).textContent = `(${userParameters.weight_gap}) кг`;
}

async function setUserStreak() {
  const userStreak = await sendData("/api/get_current_streak");
  console.log(userStreak);
  document.querySelector(
    ".strick__time"
  ).textContent = `${userStreak.current_streak} дня подряд 🥳 `;
  document.querySelector(
    ".notion__p-motivation"
  ).textContent = `${userStreak["motivational text"]}`;
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
    document.querySelector(".list").insertAdjacentHTML(
      "beforeend",
      `
      <li class="list__item">
        <span class="list__item__marker"></span>${el}
      </li>`
    );
  });
}

async function setNutrientParameters() {
  const nutrientStreak = await sendData("/api/get_nutrient_parameters");
  console.log(nutrientStreak);
  document.querySelector(
    ".day_calories"
  ).textContent = `${nutrientStreak.day_calories} ккал`;
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
  plates.forEach((plate) => {
    document.querySelector(".cards").insertAdjacentHTML(
      "afterbegin",
      `<div class="card">
    <div class="card__type">Завтрак</div>
    <div class="card__calories">310 ккал</div>
    <div class="card__meal">“Вареная курица с гречкой”</div>
    <div class="card__visual">
      <img src="../static/images/4-parts.svg" class="card__plate" />
      <div class="card__plate_frames"></div>
      <div class="card__plate_size">
        <div class="plate__arrow">
          <img src="../static/images/plate-arrow.svg" alt="" />
        </div>
        <div class="plate__size-title plate-diameter-value">
          21 см
        </div>
      </div>
    </div>
    <p class="card__list-description">Список блюд</p>
    <div class="card__list">
      <p class="card__list__item">1. Вареная курица</p>
      <p class="card__list__item">2. Вареная гречка</p>
      <p class="card__list__item">3. Помидоры</p>
    </div>
    <p class="card__difficulty">Сложность</p>
    <div class="card__stars">
      <img src="../static/images/green-star.svg" alt="" />
      <img src="../static/images/green-star.svg" alt="" />
      <img src="../static/images/green-star.svg" alt="" />
      <img src="../static/images/gray-star.svg" alt="" />
      <img src="../static/images/gray-star.svg" alt="" />
    </div>
    <p class="total-time">Общее время приготовления</p>
    <p class="total-time_value">60 минут</p>
    <p class="active-time">Активное время приготовления</p>
    <p class="active-time_value">20 минут</p>
    <div class="card__buttons">
      <button class="card__button__recepi">Рецепт</button>
      <button class="card__button__choose">Выбрать</button>
    </div>
  </div>`
    );
    document.querySelector(".card__meal").textContent = plate.plate_name;
    document.querySelector(".card__type").textContent = plate.plate_type;
    document.querySelector(".card__meal").textContent = plate.plate_name;
    document.querySelector(".card__meal").textContent = plate.plate_name;
    document.querySelector(".card__meal").textContent = plate.plate_name;
  });
}

setUserParameters();
setUserStreak();
setNutrientParameters();
setPlates();

// const userStreak = sendData("/api/get_current_streak");

// const todayPlates = sendData("/api/get_today_plates");

//  'plate_name': row.plate_name,
// 'plate_type': row.plate_type,
// 'recipe_time': row.recipe_time,
// 'recipe_active_time': row.recipe_active_time,
// 'recipe_difficulty': row.recipe_difficulty,
// 'meals': row.meal_names.split(', '),
// 'percentages': row.percentage.split(', '),
// 'calories': row.calories,
// 'proteins': row.proteins,
// 'fats': row.fats,
// 'carbohydrates': row.carbohydrates,

let tg = window.Telegram.WebApp;
let tg_id = tg.initDataUnsafe.user.id;

document.querySelector("#tg_id").value = tg_id;
